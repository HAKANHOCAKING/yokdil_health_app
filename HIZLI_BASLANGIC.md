# ⚡ YÖKDİL HEALTH APP - HIZLI BAŞLANGIÇ (5 Dakika)

## 🎯 HEDEF

Projeyi 5 dakikada çalıştır!

---

## ✅ ÖN KOŞULLAR

Sisteminizde **şunlardan biri** yüklü olmalı:
- ✅ **Docker Desktop** (ÖNERİLEN - tek komut ile tüm sistem)
- ❌ Veya: Python 3.11+ + PostgreSQL + Redis (manuel kurulum)

---

## 🚀 DOCKER İLE HIZLI BAŞLANGIÇ (ÖNERİLEN)

### 1. Docker Desktop Kur (Eğer yoksa)

```
https://www.docker.com/products/docker-desktop/
- İndir ve yükle (5 dakika)
- Docker Desktop'ı başlat
```

### 2. Projeyi Başlat (Tek Komut!)

```powershell
# Terminal aç (PowerShell)
cd C:\Users\90505\yokdil_health_app

# TÜM SİSTEMİ BAŞLAT (PostgreSQL + Redis + MinIO + Backend)
docker compose up -d

# Loglara bak (CTRL+C ile çık)
docker compose logs -f backend
```

### 3. Database Setup (İlk Kez - ZORUNLU!)

```powershell
# Backend container'a gir
docker compose exec backend bash

# Migration + Seed (İKİ KOMUT)
alembic upgrade head
python scripts/seed_trap_types.py

# Çık
exit
```

### 4. Test Et

```powershell
# Health check
curl http://localhost:8000/health

# API Docs (tarayıcıda)
start http://localhost:8000/docs
```

**✅ HAZIR! Backend çalışıyor:** http://localhost:8000

---

## 🐍 PYTHON İLE HIZLI BAŞLANGIÇ (Docker Olmadan)

### Ön Koşul: Python + PostgreSQL + Redis Yüklü Olmalı

```powershell
# Python kontrolü
python --version  # 3.11+ olmalı

# PostgreSQL kontrolü
psql --version  # 15+ olmalı

# Redis kontrolü (Windows: Memurai)
# Services.msc > Memurai service çalışıyor mu?
```

### 1. Backend Kurulum

```powershell
cd C:\Users\90505\yokdil_health_app\backend

# Virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Dependencies (2-3 dakika)
pip install -r requirements.txt

# Database oluştur (PostgreSQL'de)
# psql -U postgres
# CREATE DATABASE yokdil_db;
# \q

# .env dosyası zaten var (kontrol et)
type .env
```

### 2. Database Setup

```powershell
# Migration
alembic upgrade head

# ZORUNLU: Trap types seed (20 trap type)
python scripts\seed_trap_types.py

# Opsiyonel: Demo data
python scripts\seed_demo_data.py
```

### 3. Backend Başlat

```powershell
# Development mode
uvicorn app.main:app --reload --port 8000
```

### 4. Test Et

```powershell
# Yeni terminal aç
curl http://localhost:8000/health

# API Docs (tarayıcıda)
start http://localhost:8000/docs
```

**✅ HAZIR! Backend çalışıyor:** http://localhost:8000

---

## 📱 FLUTTER APP BAŞLAT (Opsiyonel)

### Ön Koşul: Flutter SDK Yüklü

```powershell
# Flutter kontrolü
flutter --version  # 3.19+ olmalı
```

### Başlat

```powershell
cd C:\Users\90505\yokdil_health_app\flutter_app

# Dependencies
flutter pub get

# Code generation
dart run build_runner build --delete-conflicting-outputs

# Chrome'da çalıştır
flutter run -d chrome

# Veya Android emulator
flutter run
```

---

## ✅ BAŞARILI KURULUM KONTROL LİSTESİ

- ✅ Backend çalışıyor: http://localhost:8000/health → `{"status": "healthy"}`
- ✅ API Docs açılıyor: http://localhost:8000/docs
- ✅ Trap types seeded: `SELECT COUNT(*) FROM trap_types;` → 20
- ✅ Register/Login test edildi
- ✅ Flutter app başlatıldı (opsiyonel)

---

## 🎮 İLK TESTİNİZ

### 1. Kullanıcı Kaydı (Register)

```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test Öğrenci",
    "role": "student"
  }'
```

### 2. Giriş (Login)

```powershell
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# access_token'ı kopyala
```

### 3. Profil Görüntüle

```powershell
curl http://localhost:8000/api/v1/auth/me `
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## 🆘 SORUN ÇÖZME (30 Saniye)

### Backend Başlamıyor?

```powershell
# Port 8000 kullanımda mı?
netstat -ano | findstr :8000

# Process'i öldür
taskkill /PID <PID> /F
```

### PostgreSQL Bağlanamıyor?

```powershell
# Service çalışıyor mu?
# Services.msc > postgresql-x64-15 > Start

# .env dosyasında DATABASE_URL doğru mu?
type backend\.env
```

### Trap Types Seed Hatası?

```powershell
# Zaten seeded mi?
docker compose exec backend bash
python
>>> from sqlalchemy import create_engine, text
>>> engine = create_engine("postgresql://postgres:postgres_pass_change_me@postgres:5432/yokdil_db")
>>> with engine.connect() as conn:
...     result = conn.execute(text("SELECT COUNT(*) FROM trap_types"))
...     print(result.fetchone())
(20,)  # 20 ise OK
```

---

## 🎯 SONRAKI ADIMLAR

1. ✅ Backend çalışıyor
2. ✅ Trap types seeded
3. ⏳ Demo data seed et (opsiyonel): `python scripts/seed_demo_data.py`
4. ⏳ Flutter app çalıştır
5. ⏳ Teacher dashboard test et
6. ⏳ Admin panel test et

---

## 📚 DETAYLI DÖKÜMANTASYON

- **Tam Kurulum**: `KURULUM_REHBERI.md`
- **Proje Özeti**: `FINAL_IMPLEMENTATION_SUMMARY.md`
- **Security**: `SECURITY_CHECKLIST.md`
- **Trap System**: `TRAP_SYSTEM_DOCUMENTATION.md`
- **API Docs**: http://localhost:8000/docs

---

## 🏆 BAŞARI!

```
╔══════════════════════════════════════════╗
║                                          ║
║   ✅ YÖKDİL HEALTH APP ÇALIŞIYOR!       ║
║                                          ║
║   Backend: http://localhost:8000        ║
║   API Docs: /docs                       ║
║   Version: 2.0.0 (Enterprise)           ║
║                                          ║
║   🎉 HAZIRSINIZ!                        ║
║                                          ║
╚══════════════════════════════════════════╝
```

**Toplam Süre**: ~5 dakika (Docker) veya ~10 dakika (Manuel)

**İYİ ÇALIŞMALAR!** 🚀
