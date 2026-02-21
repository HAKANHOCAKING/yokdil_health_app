# 🚀 YÖKDİL HEALTH APP - KURULUM REHBERİ (Windows)

## ✅ ÖN KOŞULLAR

Sisteminizde **Docker** veya **Python + PostgreSQL + Redis** yüklü olmalı.

---

## 📦 SEÇENEK 1: DOCKER İLE KURULUM (ÖNERİLEN - EN KOLAY)

### 1. Docker Desktop'ı Yükle

```
1. İndir: https://www.docker.com/products/docker-desktop/
2. Yükle (admin yetkisiyle)
3. Docker Desktop'ı başlat
4. WSL 2 backend'i etkinleştir (otomatik önerilecek)
5. Ayarlar > Resources > Memory: Min 4GB ayarla
```

### 2. Projeyi Başlat

```powershell
# Proje dizinine git
cd C:\Users\90505\yokdil_health_app

# Tüm servisleri başlat (PostgreSQL, Redis, MinIO, Backend)
docker compose up -d

# Logları izle
docker compose logs -f backend

# Servis durumlarını kontrol et
docker compose ps
```

### 3. Database Migration

```powershell
# Backend container'a gir
docker compose exec backend bash

# Migration'ları çalıştır
alembic upgrade head

# Trap types'ı seed et (ZORUNLU!)
python scripts/seed_trap_types.py

# (Opsiyonel) Demo data seed et
python scripts/seed_demo_data.py

# Container'dan çık
exit
```

### 4. API'yi Test Et

```powershell
# Health check
curl http://localhost:8000/health

# API Docs (Swagger)
# Tarayıcıda aç: http://localhost:8000/docs
```

### 5. Servisleri Durdur/Kaldır

```powershell
# Durdur
docker compose stop

# Tamamen kaldır (data silinmez)
docker compose down

# Data ile birlikte kaldır (DİKKAT!)
docker compose down -v
```

---

## 📦 SEÇENEK 2: MANUEL KURULUM (Docker Olmadan)

### 1. Python 3.11+ Kur

```
1. İndir: https://www.python.org/downloads/ (3.11 veya 3.12)
2. Yükle
   ✅ "Add Python to PATH" seçeneğini işaretle!
3. Doğrula:
   python --version
   pip --version
```

### 2. PostgreSQL 15+ Kur

```
1. İndir: https://www.postgresql.org/download/windows/
2. Yükle
   - Port: 5432
   - Password: postgres_pass_change_me
   - Database: yokdil_db oluştur
3. pgAdmin4 ile bağlan ve DB oluştur:
   CREATE DATABASE yokdil_db;
```

### 3. Redis Kur (Windows)

```
Memurai (Windows için Redis):
1. İndir: https://www.memurai.com/get-memurai
2. Yükle (default settings)
3. Service başlat
```

### 4. MinIO Kur (Opsiyonel - PDF upload için)

```
1. İndir: https://min.io/download
2. Çalıştır:
   minio.exe server C:\minio-data --console-address ":9001"
3. Browser: http://localhost:9001
   - User: minioadmin
   - Pass: minioadmin
```

### 5. Backend Kurulumu

```powershell
# Proje dizinine git
cd C:\Users\90505\yokdil_health_app\backend

# Virtual environment oluştur
python -m venv venv

# Aktif et
.\venv\Scripts\Activate.ps1
# Eğer hata alırsanız:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Dependencies yükle
pip install --upgrade pip
pip install -r requirements.txt

# .env dosyası zaten var (kontrol et)
type .env

# Database migration
alembic upgrade head

# ZORUNLU: Trap types seed et
python scripts\seed_trap_types.py

# (Opsiyonel) Demo data
python scripts\seed_demo_data.py
```

### 6. Backend Başlat

```powershell
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Veya
python -m uvicorn app.main:app --reload
```

### 7. Yeni Terminal'de Test Et

```powershell
# Health check
curl http://localhost:8000/health

# API Docs
# Browser: http://localhost:8000/docs
```

---

## 📱 FLUTTER APP KURULUMU

### 1. Flutter SDK Kur

```
1. İndir: https://docs.flutter.dev/get-started/install/windows
2. Extract: C:\flutter
3. Path'e ekle: C:\flutter\bin
4. Doğrula:
   flutter --version
   flutter doctor
```

### 2. Android Studio / VS Code Kur

```
Android Studio:
- Android SDK
- Android Emulator

VS Code:
- Flutter extension
- Dart extension
```

### 3. Flutter App Başlat

```powershell
cd C:\Users\90505\yokdil_health_app\flutter_app

# Dependencies
flutter pub get

# Code generation
dart run build_runner build --delete-conflicting-outputs

# Cihazları kontrol et
flutter devices

# Emulator başlat (Android Studio'dan)
# veya Chrome'da çalıştır:
flutter run -d chrome

# Veya Android emulator:
flutter run -d emulator-5554
```

---

## 🧪 TEST

### Backend Tests

```powershell
cd C:\Users\90505\yokdil_health_app\backend

# Tüm testler
pytest tests/ -v

# Coverage ile
pytest tests/ -v --cov=app --cov-report=html

# Sadece security tests
pytest tests/test_security.py -v
```

### Flutter Tests

```powershell
cd C:\Users\90505\yokdil_health_app\flutter_app

# Unit tests
flutter test

# Coverage
flutter test --coverage
```

---

## 📊 ÇALIŞAN SİSTEM KONTROLÜ

### 1. Backend Health

```powershell
curl http://localhost:8000/health

# Beklenen output:
# {
#   "status": "healthy",
#   "service": "YÖKDİL Health App",
#   "version": "2.0.0",
#   "environment": "development"
# }
```

### 2. Database Kontrol

```powershell
# PostgreSQL bağlantısı
psql -U postgres -d yokdil_db

# Tabloları listele
\dt

# Trap types kontrolü
SELECT COUNT(*) FROM trap_types;
# Beklenen: 20

# Çık
\q
```

### 3. API Endpoints Test

```powershell
# Register
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "role": "student"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

---

## 🔧 SORUN GİDERME

### Port Çakışması

```powershell
# Port 8000 kullanımda mı?
netstat -ano | findstr :8000

# Process'i öldür
taskkill /PID <PID> /F

# Veya farklı port kullan
uvicorn app.main:app --port 8001
```

### PostgreSQL Bağlantı Hatası

```
Error: could not connect to server

Çözüm:
1. PostgreSQL service çalışıyor mu?
   Services.msc > postgresql-x64-15 > Start

2. .env dosyasında DATABASE_URL doğru mu?
   postgresql://postgres:ŞIFRE@localhost:5432/yokdil_db

3. Firewall PostgreSQL'i engelliyor mu?
   Windows Defender > İzin ver
```

### Redis Bağlantı Hatası

```
Error: Connection refused to Redis

Çözüm:
1. Redis/Memurai çalışıyor mu?
   Services.msc > Memurai > Start

2. .env dosyasında REDIS_URL doğru mu?
   redis://localhost:6379/0
```

### Alembic Migration Hatası

```
Error: Can't locate revision

Çözüm:
# Migration history'yi sıfırla (DİKKAT: data silinir!)
alembic stamp head
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### OpenAI API Key Yok

```
Warning: OpenAI API key not set

Çözüm:
1. .env dosyasına ekle:
   OPENAI_API_KEY=sk-your-key-here

2. Veya test modunda çalıştır (AI features disabled)
   # AI analyzer fallback mode kullanır
```

---

## 📚 HIZLI KOMUTLAR

### Docker (ÖNERİLEN)

```powershell
# Başlat
docker compose up -d

# Logları izle
docker compose logs -f

# Durdur
docker compose stop

# Yeniden başlat
docker compose restart backend

# Temizle
docker compose down -v
```

### Manuel (Python)

```powershell
# Backend başlat
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Yeni terminal: Celery worker
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.worker.celery_app worker -l info

# Yeni terminal: Tests
cd backend
pytest tests/ -v
```

---

## 🎯 SONRAKI ADIMLAR

1. ✅ Kurulum tamamlandı
2. ⏳ Trap types seed et (ZORUNLU!)
3. ⏳ Demo data seed et (Opsiyonel)
4. ⏳ Flutter app çalıştır
5. ⏳ Test et (register, login, questions)
6. ⏳ Teacher dashboard test et
7. ⏳ Admin panel test et (PDF upload)

---

## 📞 YARDIM

- **API Docs**: http://localhost:8000/docs
- **Comprehensive Docs**: `FINAL_IMPLEMENTATION_SUMMARY.md`
- **Security Guide**: `SECURITY_CHECKLIST.md`
- **Trap System**: `TRAP_SYSTEM_DOCUMENTATION.md`

---

## ✅ BAŞARILI KURULUM KRİTERLERİ

- ✅ `curl http://localhost:8000/health` → 200 OK
- ✅ `SELECT COUNT(*) FROM trap_types` → 20
- ✅ http://localhost:8000/docs açılıyor
- ✅ Register/Login çalışıyor
- ✅ Flutter app başlatılıyor

**PROJE HAZIR!** 🎉
