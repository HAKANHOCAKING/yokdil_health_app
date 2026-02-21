# 🟣 REPLIT İLE HIZLI TEST (2 Dakika)

## Replit Nedir?
Online IDE - Tarayıcıda kod yaz, hemen çalıştır!

---

## 🚀 ADIMLAR

### 1️⃣ Replit'e Git
```
https://replit.com/
```

### 2️⃣ GitHub'dan Import Et

**Opsiyonel A: Replit'te oluştur:**
1. **"+ Create Repl"** tıkla
2. **"Import from GitHub"** seç
3. Repository URL gir (eğer GitHub'da varsa)
4. **"Import from GitHub"** tıkla

**Opsiyonel B: Manuel yükle:**
1. **"+ Create Repl"** tıkla
2. **"Python"** seç
3. Sol panel > Files > Upload klasör
4. `backend/` klasörünü yükle

### 3️⃣ Environment Variables Ayarla

Sol panel > **"Secrets"** (🔒 ikonu):

```env
DATABASE_URL = postgresql://replit:replit_password@db.thin.dev:5432/yokdil_db
SECRET_KEY = replit-demo-secret-key-min-32-chars-for-testing
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 15
ENVIRONMENT = development
ALLOWED_ORIGINS = *
REDIS_URL = redis://localhost:6379/0
```

### 4️⃣ Database Setup (Replit PostgreSQL)

Replit'te built-in PostgreSQL kullan:

1. Sol panel > **"Database"** ikonu tıkla
2. PostgreSQL başlatılır
3. Connection string otomatik oluşur
4. `DATABASE_URL` secret'ına ekle

### 5️⃣ Çalıştır

**Run** butonu tıkla veya Shell'de:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_trap_types.py
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6️⃣ Test Et

Replit otomatik bir URL verir:
```
https://yokdil-health-app.KULLANICI_ADI.repl.co
```

**Test:**
- Health: `/health`
- API Docs: `/docs`
- Register: `/api/v1/auth/register`

---

## ✅ AVANTAJLAR

- ✅ 2 dakikada hazır
- ✅ Built-in PostgreSQL
- ✅ Ücretsiz (public repl)
- ✅ Browser'da çalışır
- ✅ Anında test

## ⚠️ DEZAVANTAJLAR

- ⚠️ Sınırlı kaynak (free tier)
- ⚠️ Uyku modu (inaktif 1 saat sonra)
- ⚠️ Public repl (herkes görebilir)

---

## 🎯 HANGİSİNİ KULLANAYIM?

| Özellik | Railway | Replit | Render |
|---------|---------|--------|--------|
| **Kurulum** | 5 dk | 2 dk | 5 dk |
| **PostgreSQL** | ✅ Ücretsiz | ✅ Built-in | ✅ Ücretsiz |
| **Redis** | ✅ Opsiyonel | ⚠️ Manuel | ✅ Opsiyonel |
| **Always On** | ✅ | ❌ (uyur) | ✅ |
| **Custom Domain** | ✅ | ✅ | ✅ |
| **Maliyet** | $5/ay free | Ücretsiz | Ücretsiz |
| **Önerim** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ (test için) | ⭐⭐⭐⭐ |

**En iyi:** Railway (production-ready)
**En hızlı:** Replit (test için)

---

## 🚀 ŞİMDİ NE YAPALIM?

**Seçenek 1: Railway (Önerilen)**
```
1. DEPLOY_RAILWAY.md dosyasını aç
2. Adımları takip et
3. 5 dakikada online!
```

**Seçenek 2: Replit (Hızlı Test)**
```
1. https://replit.com/ git
2. Import from GitHub
3. Run!
```

**Seçenek 3: Render.com (Alternatif)**
```
1. https://render.com/ git
2. New > Web Service
3. Connect GitHub repo
4. Deploy!
```

---

## 📱 FRONTEND (Flutter Web)

Backend deploy olduktan sonra:

```bash
cd flutter_app
flutter build web --release

# Vercel'e deploy:
# 1. build/web/ klasörünü zip'le
# 2. https://vercel.com/ git
# 3. Upload zip
# 4. Deploy!
```

---

## ✅ BAŞARILI DEPLOY

Backend online olduğunda:

```bash
# Health check
curl https://your-app.railway.app/health

# Register test
curl -X POST https://your-app.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@test.com",
    "password": "Test123!",
    "full_name": "Demo User",
    "role": "student",
    "tenant_id": "00000000-0000-0000-0000-000000000001"
  }'
```

---

## 🎉 HAZIR!

Proje web'de çalışıyor! 🚀

- ✅ Backend online
- ✅ PostgreSQL bağlı
- ✅ API endpoints hazır
- ✅ Trap types seeded
- ✅ Test edilebilir

**Seçtiğiniz platforma göre deploy edin ve test edin!**
