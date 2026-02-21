# 🟦 RENDER.COM İLE DEPLOY (5 Dakika)

## 1️⃣ RENDER HESABI OLUŞTUR

```
https://render.com/
Sign Up > GitHub ile giriş
```

---

## 2️⃣ POSTGRESQL EKLE

1. Dashboard > **"New +"**
2. **"PostgreSQL"**
3. Name: `yokdil-db`
4. Region: Frankfurt (en yakın)
5. **Free** tier seç
6. **"Create Database"**
7. **Internal Database URL** kopyala

---

## 3️⃣ BACKEND WEB SERVICE OLUŞTUR

1. Dashboard > **"New +"**
2. **"Web Service"**
3. **"Build and deploy from a Git repository"**
4. GitHub repo seç: `yokdil-health-app`
5. Ayarlar:

**Name:** `yokdil-backend`

**Region:** Frankfurt

**Branch:** `main`

**Root Directory:** `backend`

**Environment:** Python 3

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
alembic upgrade head && python scripts/seed_trap_types.py || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:** Free

---

## 4️⃣ ENVIRONMENT VARIABLES

Web Service > **"Environment"** sekmesi > **"Add Environment Variable"**:

```env
# Database (PostgreSQL'den kopyala)
DATABASE_URL = postgresql://user:pass@dpg-xxx.frankfurt-postgres.render.com/yokdil_db_xxx

# JWT Secret
SECRET_KEY = render-production-secret-key-min-32-chars-change-me
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

# CORS
ALLOWED_ORIGINS = https://yokdil-backend.onrender.com,http://localhost:3000

# Environment
ENVIRONMENT = production
ENABLE_HSTS = true
LOG_LEVEL = INFO

# Redis (opsiyonel - Render'da eklenebilir)
REDIS_URL = redis://red-xxx:6379

# OpenAI (opsiyonel)
OPENAI_API_KEY = sk-your-key
OPENAI_MODEL = gpt-4-turbo-preview

# Security
HSTS_MAX_AGE = 31536000
MAX_UPLOAD_SIZE_MB = 100

# Data retention
AUDIT_LOG_RETENTION_DAYS = 730
ATTEMPT_RETENTION_DAYS = 365
```

**"Save Changes"** tıkla → Otomatik deploy başlar

---

## 5️⃣ REDIS EKLE (Opsiyonel)

1. Dashboard > **"New +"**
2. **"Redis"**
3. Name: `yokdil-redis`
4. Region: Frankfurt
5. **Free** tier
6. **"Create Redis"**
7. **Internal Redis URL** kopyala
8. Backend Environment Variables'a `REDIS_URL` olarak ekle

---

## 6️⃣ TEST ET

### Deploy Tamamlandı mı?
Dashboard > yokdil-backend > **"Logs"** sekmesi:
- "Live" yazısı görünür
- Hata yok mu kontrol et

### Health Check
```
https://yokdil-backend.onrender.com/health
```

**Beklenen:**
```json
{
  "status": "healthy",
  "service": "YÖKDİL Health App",
  "version": "2.0.0",
  "environment": "production"
}
```

### API Docs (Development'ta)
```
https://yokdil-backend.onrender.com/docs
```
(Production'da kapalı)

### İlk Kullanıcı
```bash
curl -X POST https://yokdil-backend.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "DemoPass123!",
    "full_name": "Demo User",
    "role": "student",
    "tenant_id": "00000000-0000-0000-0000-000000000001"
  }'
```

---

## 7️⃣ CUSTOM DOMAIN (Opsiyonel)

1. Web Service > **"Settings"**
2. **"Custom Domains"**
3. Domain ekle: `api.yokdil-app.com`
4. DNS ayarlarını yap (CNAME)
5. SSL otomatik oluşur

---

## 🎯 RENDER ÜCRETSİZ LİMİTLER

- ✅ **PostgreSQL** (1 GB)
- ✅ **Redis** (25 MB)
- ✅ **750 saat/ay** free compute
- ✅ **Auto-deploy** (GitHub push'ta)
- ✅ **Otomatik SSL**
- ✅ **Custom domains**
- ⚠️ **Uyku modu** (15 dk inaktif sonra)

---

## 🆘 SORUN GİDERME

### Build Hatası
Logs sekmesinde:
```
ERROR: Could not find a version that satisfies the requirement XXX
```

**Çözüm:** `requirements.txt` kontrol et, versiyon çakışması var mı?

### Migration Hatası
```
ERROR: relation "users" does not exist
```

**Çözüm:** 
1. Web Service > **"Shell"** sekmesi
2. Çalıştır:
```bash
cd backend
alembic upgrade head
python scripts/seed_trap_types.py
```

### Database Bağlantı Hatası
```
ERROR: could not connect to server
```

**Çözüm:**
- `DATABASE_URL` doğru mu? (Internal URL kullan)
- PostgreSQL servisi çalışıyor mu?
- Firewall kuralları kontrol et

### Port Hatası
```
ERROR: [Errno 98] Address already in use
```

**Çözüm:** Render otomatik `$PORT` verir, `--port $PORT` kullan

---

## 📊 KARŞILAŞTIRMA

| Özellik | Railway | Render | Replit |
|---------|---------|--------|--------|
| **Kurulum** | 5 dk | 5 dk | 2 dk |
| **PostgreSQL** | 100 MB | 1 GB ✅ | Built-in |
| **Redis** | 25 MB | 25 MB | Manuel |
| **Uyku Modu** | ❌ | ✅ (15 dk) | ✅ (1 saat) |
| **Custom Domain** | ✅ | ✅ | ✅ |
| **Auto Deploy** | ✅ | ✅ | ⚠️ |
| **Maliyet** | $5/ay free | Free | Free |
| **Önerim** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

**Railway:** Always-on, production-ready
**Render:** Daha fazla storage, uyku modu var
**Replit:** En hızlı test, sınırlı

---

## ✅ BAŞARILI DEPLOY KONTROLÜ

- ✅ `/health` → 200 OK
- ✅ PostgreSQL bağlı
- ✅ Trap types seeded (logs'ta göreceksin)
- ✅ Register/Login çalışıyor
- ✅ Logs'ta hata yok

---

## 🎉 TAMAMLANDI!

```
╔════════════════════════════════════════════╗
║                                            ║
║   ✅ BACKEND RENDER'DA ÇALIŞIYOR!         ║
║                                            ║
║   URL: https://yokdil-backend.onrender.com║
║   Health: /health                         ║
║   API: /api/v1/                           ║
║                                            ║
║   • PostgreSQL 1 GB ✅                    ║
║   • Auto-Deploy ✅                        ║
║   • SSL ✅                                ║
║                                            ║
║   🚀 PROJE ONLINE!                        ║
║                                            ║
╚════════════════════════════════════════════╝
```

**Dashboard:** https://dashboard.render.com/

**İlk request 15-30 saniye sürebilir (uyku modundan uyanma)**
