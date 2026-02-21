# Quick Start Guide - 5 Dakikada Başlayın

## Ön Koşullar

- Python 3.11+
- Flutter 3.19+
- PostgreSQL 15+
- Docker & Docker Compose (opsiyonel ama önerilen)

## Hızlı Kurulum (Docker ile)

### 1. Projeyi Klonla
```bash
git clone <repo-url>
cd yokdil_health_app
```

### 2. Tüm Servisleri Başlat
```bash
docker-compose up -d
```

✅ Bu komut şunları başlatır:
- PostgreSQL veritabanı (port 5432)
- MinIO storage (port 9000, 9001)
- Redis cache (port 6379)
- FastAPI backend (port 8000)

### 3. Backend'i Test Et
```bash
curl http://localhost:8000/health

# Beklenen sonuç:
# {"status":"healthy","service":"YÖKDİL Health App","version":"1.0.0"}
```

### 4. API Dokümantasyonunu Görüntüle
Tarayıcıda aç: http://localhost:8000/docs

### 5. Flutter Uygulamasını Başlat
```bash
cd flutter_app
cp .env.example .env
flutter pub get
dart run build_runner build --delete-conflicting-outputs
flutter run
```

🎉 **Hazır!** Uygulama çalışıyor.

---

## Manuel Kurulum (Docker olmadan)

### Backend Setup

1. **Veritabanını Oluştur**
```bash
# PostgreSQL'e bağlan
psql -U postgres

# Veritabanını oluştur
CREATE DATABASE yokdil_db;
\q
```

2. **Backend Bağımlılıklarını Yükle**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

3. **Environment Variables Ayarla**
```bash
cp .env.example .env
# .env dosyasını düzenle
```

4. **Migration'ları Çalıştır**
```bash
alembic upgrade head
```

5. **Backend'i Başlat**
```bash
uvicorn app.main:app --reload
```

### Flutter Setup

1. **Bağımlılıkları Yükle**
```bash
cd flutter_app
flutter pub get
```

2. **Code Generation**
```bash
dart run build_runner build --delete-conflicting-outputs
```

3. **Environment Ayarla**
```bash
cp .env.example .env
# .env içinde API_BASE_URL'i düzenle
```

4. **Uygulamayı Çalıştır**
```bash
# Android emulator veya iOS simulator açık olmalı
flutter run
```

---

## İlk Test - Demo Kullanıcı Oluştur

### 1. Backend API ile Kayıt Ol
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "DemoPass123!",
    "full_name": "Demo Kullanıcı",
    "role": "student"
  }'
```

### 2. Login ve Token Al
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "DemoPass123!"
  }'

# Response'dan access_token'ı kopyala
```

### 3. Kullanıcı Bilgilerini Getir
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your-access-token>"
```

---

## Demo Veri Ekle (Opsiyonel)

### Python Script ile Demo Sorular Ekle
```python
# backend/scripts/seed_demo_data.py
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.question import Question, Option, Tag

async def seed_demo_data():
    async with AsyncSessionLocal() as db:
        # Örnek soru oluştur
        question = Question(
            exam_date="Mart 2018",
            question_no=1,
            stem_text="Recent studies suggest that regular physical activity ------- the risk of developing chronic diseases.",
            blank_position=8,
            difficulty="medium",
        )
        db.add(question)
        await db.commit()
        await db.refresh(question)
        
        # Seçenekleri ekle
        options = [
            Option(question_id=question.id, option_letter="A", option_text="reduces", is_correct=True),
            Option(question_id=question.id, option_letter="B", option_text="increases", is_correct=False),
            Option(question_id=question.id, option_letter="C", option_text="prevents", is_correct=False),
            Option(question_id=question.id, option_letter="D", option_text="eliminates", is_correct=False),
            Option(question_id=question.id, option_letter="E", option_text="avoids", is_correct=False),
        ]
        
        for opt in options:
            db.add(opt)
        
        await db.commit()
        print("✅ Demo veri eklendi!")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
```

Çalıştır:
```bash
cd backend
python scripts/seed_demo_data.py
```

---

## Sık Karşılaşılan Sorunlar

### Backend başlamıyor
```bash
# Veritabanı bağlantısını kontrol et
psql -h localhost -U postgres -d yokdil_db

# .env dosyasında DATABASE_URL'i doğrula
```

### Flutter build hataları
```bash
# Clean ve rebuild
flutter clean
flutter pub get
dart run build_runner clean
dart run build_runner build --delete-conflicting-outputs
```

### Kod değişiklikleri yansımıyor
```bash
# Hot reload: 'r' tuşu
# Hot restart: 'R' tuşu
# Tam yeniden başlat: 'Ctrl+C' sonra flutter run
```

### CORS hatası alıyorum
```bash
# Backend .env dosyasında ALLOWED_ORIGINS'e Flutter'ın çalıştığı adresi ekle
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5000
```

---

## Sonraki Adımlar

1. ✅ Uygulamayı çalıştırdın
2. 📚 [README.md](README.md) dosyasını oku (detaylı mimari)
3. 🔧 [DEPLOYMENT.md](DEPLOYMENT.md) dosyasını oku (production deployment)
4. 🧪 Test'leri çalıştır: `pytest backend/tests`
5. 📖 API dokümantasyonunu keşfet: http://localhost:8000/docs
6. 🎨 Flutter widget'larını özelleştir

---

## Demo Akış

1. **Login/Register** → Ana sayfa
2. **Sınav Modu** seç → 10 soru çöz → Sonuçları gör
3. **İstatistikler** → Performansını analiz et
4. **Soru Bankası** → Tüm soruları filtrele/ara

Herhangi bir sorun mu var? GitHub Issues'ta sor veya iletişime geç!
