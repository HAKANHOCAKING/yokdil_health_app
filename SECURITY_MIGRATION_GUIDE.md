# Security Migration Guide

## 🔄 Mevcut MVP'den Enterprise Security'ye Geçiş

Bu guide, mevcut MVP kodundan yeni güvenlik katmanlarına geçiş için adım adım talimatlar içerir.

---

## 📋 ADIM 1: Bağımlılıklar Güncellemesi

### Backend Requirements
```bash
cd backend

# Yeni requirements.txt'i kullan (Argon2, Celery, user-agents eklenmiş)
pip install -r requirements.txt

# Önemli: argon2-cffi, celery[redis], user-agents yüklenmiş olmalı
```

---

## 📋 ADIM 2: Database Migration

### Yeni Tablolar
Aşağıdaki tablolar eklendi:
1. `tenants` - Multi-tenancy için kurum bilgileri
2. `session_devices` - Cihaz bazlı oturum takibi
3. `refresh_tokens` - Token rotation için
4. `audit_logs` - Audit logging
5. Mevcut tablolara `tenant_id` kolonu eklendi

### Migration Script Çalıştırma
```bash
cd backend

# Yeni migration oluştur
alembic revision --autogenerate -m "Add enterprise security features"

# Migration'ı incele ve düzenle (gerekirse)
nano alembic/versions/xxx_add_enterprise_security_features.py

# Migration'ı uygula
alembic upgrade head
```

### Manual Migration (Gerekirse)
```sql
-- 1. Tenants tablosu oluştur
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP,
    max_users INTEGER DEFAULT 100,
    max_storage_gb INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    settings JSONB
);

-- 2. Varsayılan tenant oluştur (mevcut users için)
INSERT INTO tenants (id, name) VALUES 
('00000000-0000-0000-0000-000000000001', 'Default Institution');

-- 3. Users tablosuna tenant_id ekle
ALTER TABLE users ADD COLUMN tenant_id UUID REFERENCES tenants(id);
UPDATE users SET tenant_id = '00000000-0000-0000-0000-000000000001';
ALTER TABLE users ALTER COLUMN tenant_id SET NOT NULL;
CREATE INDEX idx_users_tenant_id ON users(tenant_id);

-- 4. Diğer tablolara tenant_id ekle
ALTER TABLE questions ADD COLUMN tenant_id UUID REFERENCES tenants(id);
UPDATE questions SET tenant_id = '00000000-0000-0000-0000-000000000001';
ALTER TABLE questions ALTER COLUMN tenant_id SET NOT NULL;

ALTER TABLE classes ADD COLUMN tenant_id UUID REFERENCES tenants(id);
UPDATE classes SET tenant_id = '00000000-0000-0000-0000-000000000001';
ALTER TABLE classes ALTER COLUMN tenant_id SET NOT NULL;

-- (Diğer tablolar için tekrarla: sessions, assignments, vb.)

-- 5. Session devices tablosu
CREATE TABLE session_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL UNIQUE,
    device_type VARCHAR(50),
    os VARCHAR(100),
    browser VARCHAR(100),
    ip_address VARCHAR(45),
    last_active_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);
CREATE INDEX idx_session_devices_user_id ON session_devices(user_id);
CREATE INDEX idx_session_devices_device_id ON session_devices(device_id);

-- 6. Refresh tokens tablosu
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL REFERENCES session_devices(device_id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP,
    is_valid BOOLEAN DEFAULT TRUE,
    replaced_by UUID REFERENCES refresh_tokens(id)
);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);

-- 7. Audit logs tablosu
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    user_email VARCHAR(255),
    user_role VARCHAR(50),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    description TEXT,
    changes JSONB,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    device_id VARCHAR(255),
    request_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT
);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
```

---

## 📋 ADIM 3: Mevcut Şifreleri Argon2'ye Migrate Et

Mevcut bcrypt şifreleri Argon2'ye geçiş için script:

```python
# backend/scripts/migrate_passwords.py
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def migrate_passwords():
    """
    SECURITY: Migrate bcrypt passwords to Argon2
    NOTE: Requires users to login once to update
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        print(f"Found {len(users)} users")
        print("⚠️  Password migration will happen on next login")
        print("    Old bcrypt hashes remain valid until user logs in")
        
        # Migration happens automatically on login in auth endpoint
        # Because verify_password() handles both bcrypt and argon2

if __name__ == "__main__":
    asyncio.run(migrate_passwords())
```

**NOT**: Şifre migration'ı otomatik olur. `passlib` her iki formatı da destekler, kullanıcı login olduğunda otomatik Argon2'ye geçer.

---

## 📋 ADIM 4: Environment Variables Güncelleme

`.env` dosyasını güncelleyin:

```env
# Mevcut değişkenler...

# YENİ: Short-lived access tokens (15 dakika)
ACCESS_TOKEN_EXPIRE_MINUTES=15

# YENİ: HSTS
ENABLE_HSTS=true
HSTS_MAX_AGE=31536000

# YENİ: File upload limitleri
MAX_UPLOAD_SIZE_MB=50

# YENİ: Data retention (KVKK)
AUDIT_LOG_RETENTION_DAYS=730
ATTEMPT_RETENTION_DAYS=365

# YENİ: MFA (opsiyonel)
ENABLE_MFA=false
```

---

## 📋 ADIM 5: Celery Worker Başlatma

### Development
```bash
cd backend

# Celery worker başlat
celery -A app.worker.celery_app worker --loglevel=info

# (Ayrı terminal) Flower monitoring (opsiyonel)
celery -A app.worker.celery_app flower --port=5555
```

### Production (Supervisor ile)
```ini
# /etc/supervisor/conf.d/celery.conf
[program:celery]
command=/path/to/venv/bin/celery -A app.worker.celery_app worker --loglevel=info
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log
```

---

## 📋 ADIM 6: Endpoint Değişiklikleri

### Auth Endpoints - YENİ
```python
# Token refresh ile device tracking
POST /api/v1/auth/refresh
{
  "refresh_token": "...",
  "device_id": "..."  # YENİ: Client device ID
}

# Logout all devices
POST /api/v1/auth/logout-all-devices

# Get user sessions
GET /api/v1/auth/sessions
```

### KVKK Endpoints - YENİ
```python
# Data export
POST /api/v1/kvkk/data-export-request
GET /api/v1/kvkk/data-export/{export_id}

# Data deletion
POST /api/v1/kvkk/data-deletion-request
{"confirmation": "DELETE_MY_DATA"}

# Data summary
GET /api/v1/kvkk/my-data-summary
```

---

## 📋 ADIM 7: Frontend (Flutter) Değişiklikleri

### Device ID Generation
```dart
// lib/core/device/device_id.dart
import 'package:uuid/uuid.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class DeviceIdService {
  final _storage = const FlutterSecureStorage();
  static const _key = 'device_id';

  Future<String> getDeviceId() async {
    String? deviceId = await _storage.read(key: _key);
    
    if (deviceId == null) {
      deviceId = const Uuid().v4();
      await _storage.write(key: _key, value: deviceId);
    }
    
    return deviceId;
  }
}
```

### Updated Login
```dart
Future<void> login(String email, String password) async {
  final deviceId = await DeviceIdService().getDeviceId();
  
  final response = await _repository.login(
    email,
    password,
    deviceId: deviceId,  // YENİ parametre
  );
  
  // Store tokens
  await _apiClient.saveTokens(
    response['access_token'],
    response['refresh_token'],
  );
}
```

---

## 📋 ADIM 8: Test Çalıştırma

### Security Tests
```bash
cd backend

# Sadece security testlerini çalıştır
pytest tests/test_security.py -v

# Tüm testler
pytest tests/ -v --cov=app
```

### Test Sonuçları (Beklenen)
- ✅ `test_student_cannot_access_other_student_data`
- ✅ `test_teacher_cannot_access_other_class_data`
- ✅ `test_cross_tenant_data_isolation`
- ✅ `test_token_reuse_detection`
- ✅ `test_rate_limiting_login`
- ✅ `test_argon2_password_hashing`
- ✅ `test_admin_cannot_access_other_tenant`

---

## 📋 ADIM 9: Monitoring Setup

### Sentry (Error Tracking)
```python
# backend/app/main.py içinde zaten var
import sentry_sdk
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
)
```

### Audit Log Monitoring
```sql
-- Suspicious activity query
SELECT * FROM audit_logs
WHERE status = 'failure'
AND action LIKE 'auth_%'
AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY user_id
HAVING COUNT(*) > 5;  -- 5+ failed attempts in 1 hour
```

---

## 📋 ADIM 10: Production Deployment

### Pre-deployment Checklist
```bash
# 1. Environment variables production'da set edildi mi?
# 2. Database backup alındı mı?
# 3. SSL certificate kuruldu mu?
# 4. CORS origins production domains ile güncellendi mi?
# 5. SECRET_KEY yeterince güçlü mü? (min 32 chars)
# 6. Celery worker çalışıyor mu?
# 7. Redis çalışıyor mu?
# 8. Security tests pass ediyor mu?

# Security scan (opsiyonel)
bandit -r app/
safety check
```

---

## 🚨 BREAKING CHANGES

### 1. Access Token TTL
- **Eski**: 60 dakika
- **Yeni**: 15 dakika (daha güvenli)
- **Etki**: Mobile app daha sık refresh yapmalı

### 2. Tenant ID Zorunlu
- **Değişiklik**: Tüm users, questions, vb. `tenant_id` gerektiriyor
- **Çözüm**: Migration script default tenant oluşturuyor

### 3. Password Hashing
- **Eski**: bcrypt
- **Yeni**: Argon2id
- **Etki**: Login sırasında otomatik migrate oluyor

### 4. Refresh Token Rotation
- **Değişiklik**: Her refresh'te token değişiyor
- **Etki**: Token reuse detect ediliyor ve tüm sessions invalid oluyor

---

## 📚 Kaynaklar

- Security Checklist: `SECURITY_CHECKLIST.md`
- API Documentation: http://localhost:8000/docs
- Audit Log Schema: `app/models/audit_log.py`
- Security Tests: `tests/test_security.py`

---

## ❓ Sorun Giderme

### Problem: Migration hataları
```bash
# Migration'ı rollback et
alembic downgrade -1

# Yeniden oluştur
alembic revision --autogenerate -m "Fix migration"
alembic upgrade head
```

### Problem: Celery worker başlamıyor
```bash
# Redis bağlantısını kontrol et
redis-cli ping

# Celery debug mode
celery -A app.worker.celery_app worker --loglevel=debug
```

### Problem: Argon2 yavaş
```python
# config.py içinde cost parametreleri ayarla
argon2__memory_cost=32768,  # 64MB -> 32MB
argon2__time_cost=2,        # 3 -> 2
```

---

**Geçiş Süresi**: ~2-4 saat (development), ~1 gün (production testing dahil)
**Risk Seviyesi**: Orta (database migration gerekiyor, ancak backward compatible)
**Rollback**: Mümkün (database backup ile)
