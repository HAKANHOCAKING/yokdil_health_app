# YÖKDİL Sağlık Cümle Tamamlama Uygulaması

Modern, AI-destekli, çevrimdışı çalışabilen YÖKDİL Sağlık sınavı hazırlık uygulaması.

## 🏗️ Mimari

- **Frontend**: Flutter (iOS + Android + Web Admin Panel)
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **Local DB**: Drift (SQLite)
- **Storage**: MinIO (S3-compatible)
- **State Management**: Riverpod
- **Architecture**: Clean Architecture (Presentation/Domain/Data)

## 📁 Proje Yapısı

```
yokdil_health_app/
├── flutter_app/              # Flutter mobil uygulama
│   ├── lib/
│   │   ├── core/             # Shared utilities
│   │   ├── features/         # Feature-based modules
│   │   │   ├── auth/
│   │   │   ├── questions/
│   │   │   ├── sessions/
│   │   │   ├── analytics/
│   │   │   └── admin/
│   │   └── main.dart
│   ├── test/
│   └── pubspec.yaml
├── admin_web/                # Flutter Web admin paneli
│   └── ...
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/              # API routers
│   │   ├── core/             # Config, security, db
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── pdf_parser.py
│   │   │   ├── trap_analyzer.py
│   │   │   └── question_generator.py
│   │   └── main.py
│   ├── alembic/              # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## 🚀 Kurulum

### Gereksinimler

- Flutter SDK 3.19+
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (opsiyonel)
- MinIO server

### Backend Kurulumu

```bash
cd backend

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# .env dosyasını düzenle

# Database migration
alembic upgrade head

# Sunucuyu başlat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Flutter App Kurulumu

```bash
cd flutter_app

# Bağımlılıkları yükle
flutter pub get

# Drift code generation
dart run build_runner build --delete-conflicting-outputs

# Android emulator'da çalıştır
flutter run

# iOS'ta çalıştır (macOS gerekli)
flutter run -d ios
```

### Docker ile Kurulum (Önerilen)

```bash
# Tüm servisleri başlat (Postgres, MinIO, Backend, Flutter Web)
docker-compose up -d

# Logları izle
docker-compose logs -f

# Durdur
docker-compose down
```

## 🔑 Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/yokdil_db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=yokdil-pdfs

# OpenAI (for AI features)
OPENAI_API_KEY=sk-...

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Flutter (.env)

```env
API_BASE_URL=http://localhost:8000/api/v1
ENVIRONMENT=development
```

## 📝 API Documentation

Backend çalıştığında otomatik OpenAPI docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Flutter Tests

```bash
cd flutter_app

# Unit tests
flutter test

# Widget tests
flutter test test/widget_test.dart

# Integration tests
flutter test integration_test/
```

## 📊 Database Migration

```bash
cd backend

# Yeni migration oluştur
alembic revision --autogenerate -m "Migration açıklaması"

# Migration uygula
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🎯 Özellikler

### MVP (Aşama 1)
- ✅ JWT Authentication (Student, Teacher, Admin roles)
- ✅ PDF upload ve otomatik parsing
- ✅ Soru bankası CRUD
- ✅ Sınav modu (timer, no hints)
- ✅ Koçluk modu (instant feedback)
- ✅ Offline mode (Drift SQLite)
- ✅ Basic analytics

### Aşama 2
- ✅ ÖSYM Tuzak Analiz Motoru
- ✅ Trap heatmap (topic × trap type)
- ✅ Spaced repetition (SM-2 algoritması)
- ✅ Teacher dashboard
- ✅ Assignment system
- ✅ Advanced analytics

### Aşama 3 (PRO)
- ⏳ AI question generator
- ⏳ Multi-language support (TR/EN explanations)
- ⏳ Gamification (achievements, leaderboards)
- ⏳ Apple/Google Sign-In
- ⏳ Push notifications
- ⏳ Video explanations

## 🔐 Güvenlik

- JWT-based authentication
- Password hashing (bcrypt)
- Rate limiting (SlowAPI)
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection
- HTTPS enforced in production
- KVKK compliant (data export/delete endpoints)

## 🛠️ Teknoloji Stack Detayları

### Backend
- **FastAPI**: Modern, hızlı async web framework
- **SQLAlchemy 2.0**: ORM
- **Alembic**: Database migrations
- **Pydantic V2**: Data validation
- **python-jose**: JWT tokens
- **passlib**: Password hashing
- **pdfplumber**: PDF parsing
- **pytesseract**: OCR fallback
- **openai**: AI features
- **slowapi**: Rate limiting
- **boto3**: S3/MinIO client

### Flutter
- **riverpod**: State management
- **drift**: Local database
- **dio**: HTTP client
- **flutter_secure_storage**: Token storage
- **json_serializable**: JSON serialization
- **cached_network_image**: Image caching
- **fl_chart**: Analytics charts
- **shimmer**: Loading animations

## 📈 Performans Hedefleri

- API response time: < 200ms (p95)
- Flutter UI: 60fps sabit
- PDF parsing: < 30s per 100-page document
- Offline mode: Full functionality
- Cold start: < 2s

## 📄 Lisans

Bu proje eğitim amaçlıdır. PDF içeriklerin telif hakları yayıncılara aittir.

## 👥 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişiklikleri commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

Sorular için: [Email/GitHub Issues]

---

**Not**: Production deployment için `docker-compose.prod.yml` ve environment-specific configs kullanın.
