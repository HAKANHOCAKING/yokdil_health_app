# 🚀 YÖKDİL HEALTH APP - SİSTEMİ BAŞLAT

## ⚡ HIZLI BAŞLANGIÇ (3 ADIM)

### 1️⃣ SİSTEM KONTROLÜ
```powershell
# PowerShell aç (Admin yetkisiyle)
cd C:\Users\90505\yokdil_health_app

# Tüm gereksinimleri kontrol et
.\check-system.ps1
```

**Beklenen Çıktı:**
```
✅ Python 3.11+
✅ PostgreSQL Çalışıyor
✅ Redis/Memurai Çalışıyor
✅ .env dosyası mevcut
```

**Eğer eksik varsa:**
- Python yok → https://www.python.org/downloads/
- PostgreSQL yok → https://www.postgresql.org/download/windows/
- Redis yok → https://www.memurai.com/get-memurai
- .env yok → `Copy-Item backend\.env.example backend\.env`

---

### 2️⃣ DATABASE SETUP (İLK KEZ)
```powershell
# İlk kurulumda bir kez çalıştırın
.\setup-database.ps1

# Bu script:
# - Alembic migration çalıştırır
# - 20 trap type seed eder (ZORUNLU!)
# - Demo data seed eder (opsiyonel)
```

**Beklenen Çıktı:**
```
✅ Migration tamamlandı
✅ Trap types seed edildi (20)
✅ DATABASE SETUP TAMAMLANDI!
```

---

### 3️⃣ BACKEND BAŞLAT
```powershell
# Backend'i başlat
.\start-backend.ps1

# Bu script:
# - Virtual environment oluşturur/aktif eder
# - Dependencies yükler
# - Database migration kontrol eder
# - Backend'i başlatır (uvicorn)
```

**Beklenen Çıktı:**
```
✅ TÜM KONTROLLER TAMAMLANDI!
Backend başlatılıyor...
API Docs: http://localhost:8000/docs
Health: http://localhost:8000/health
```

---

## ✅ BAŞARILI KURULUM KONTROLÜ

### 1. Health Check
```powershell
# Yeni terminal aç
curl http://localhost:8000/health

# Beklenen:
# {
#   "status": "healthy",
#   "service": "YÖKDİL Health App",
#   "version": "2.0.0"
# }
```

### 2. API Docs
```
Tarayıcıda aç: http://localhost:8000/docs
```

### 3. İlk Kullanıcı Kaydı
```powershell
# Test kullanıcısı oluştur
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test Kullanıcı",
    "role": "student",
    "tenant_id": "00000000-0000-0000-0000-000000000001"
  }'
```

---

## 🎮 SONRAKI ADIMLAR

### A) Flutter App Başlat (Opsiyonel)
```powershell
cd flutter_app

# Dependencies
flutter pub get

# Code generation
dart run build_runner build --delete-conflicting-outputs

# Chrome'da çalıştır
flutter run -d chrome
```

### B) Celery Worker Başlat (Background Tasks)
```powershell
# Yeni terminal aç
cd backend
.\venv\Scripts\Activate.ps1

# Celery worker
celery -A app.worker.celery_app worker -l info -Q pdf,ai,export
```

### C) Test Çalıştır
```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Tüm testler
pytest tests/ -v

# Sadece security tests
pytest tests/test_security.py -v

# Coverage ile
pytest tests/ -v --cov=app --cov-report=html
```

---

## 🆘 SORUN GİDERME

### Backend Başlamıyor

**Port 8000 kullanımda:**
```powershell
# Port'u kullanan process'i bul ve öldür
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**PostgreSQL Bağlanamıyor:**
```powershell
# Servis çalışıyor mu?
Get-Service postgresql*

# Başlat
Start-Service postgresql-x64-15
```

**Redis Bağlanamıyor:**
```powershell
# Servis çalışıyor mu?
Get-Service Memurai*

# Başlat
Start-Service Memurai
```

### Migration Hatası

```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Migration history'yi kontrol et
alembic current

# Sıfırdan migration (DİKKAT: Data silinir!)
alembic downgrade base
alembic upgrade head
```

### Trap Types Seed Hatası

```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Manuel seed
python scripts\seed_trap_types.py

# Kontrol et
python -c "from sqlalchemy import create_engine, text; from app.core.config import settings; engine = create_engine(settings.DATABASE_URL); with engine.connect() as conn: result = conn.execute(text('SELECT COUNT(*) FROM trap_types')); print('Trap types:', result.fetchone()[0])"

# Beklenen: Trap types: 20
```

---

## 📁 ÖNEML İ DOSYALAR

```
yokdil_health_app/
├── check-system.ps1           ← Sistem kontrolü
├── setup-database.ps1         ← İlk database setup
├── start-backend.ps1          ← Backend başlat
├── backend/
│   ├── .env                   ← Konfigürasyon (SECRET!)
│   ├── requirements.txt       ← Python dependencies
│   ├── alembic/               ← Database migrations
│   ├── scripts/
│   │   ├── seed_trap_types.py ← 20 trap type seed
│   │   └── seed_demo_data.py  ← Demo data seed
│   └── app/
│       ├── main.py            ← FastAPI app
│       ├── models/            ← Database models
│       ├── api/               ← API endpoints
│       └── services/          ← Business logic
└── flutter_app/               ← Mobile app
```

---

## 🎯 BAŞARILI KURULUM ÖZETİ

✅ Backend çalışıyor: http://localhost:8000
✅ API Docs: http://localhost:8000/docs
✅ Database migration tamamlandı
✅ 20 trap type seed edildi
✅ Test kullanıcısı oluşturuldu
✅ Sistem hazır!

---

## 📚 DETAYLI DOKÜMANTASYON

- **Kurulum**: `KURULUM_REHBERI.md`
- **Hızlı Başlangıç**: `HIZLI_BASLANGIC.md`
- **Proje Özeti**: `FINAL_IMPLEMENTATION_SUMMARY.md`
- **Security**: `SECURITY_CHECKLIST.md`
- **Trap System**: `TRAP_SYSTEM_DOCUMENTATION.md`
- **API Docs**: http://localhost:8000/docs

---

## 🏆 BAŞARILI! SİSTEM ÇALIŞIYOR!

```
╔═══════════════════════════════════════════╗
║                                           ║
║   ✅ YÖKDİL HEALTH APP HAZIR!            ║
║                                           ║
║   Backend: http://localhost:8000         ║
║   API Docs: /docs                        ║
║   Version: 2.0.0 (Enterprise)            ║
║                                           ║
║   • 180+ Features                        ║
║   • 20 Trap Types                        ║
║   • Enterprise Security                  ║
║   • KVKK Compliant                       ║
║                                           ║
║   🚀 İYİ ÇALIŞMALAR!                     ║
║                                           ║
╚═══════════════════════════════════════════╝
```

---

**Son Güncelleme**: 2024-02-17
**Versiyon**: 2.0.0
**Durum**: ✅ Production-Ready
