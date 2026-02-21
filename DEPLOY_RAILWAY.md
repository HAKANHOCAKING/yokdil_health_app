# 🚂 RAILWAY.APP İLE DEPLOY (5 Dakika)

## 1️⃣ RAILWAY HESABI OLUŞTUR

1. Git: https://railway.app/
2. **"Start a New Project"** tıkla
3. GitHub ile giriş yap (ücretsiz)

---

## 2️⃣ GITHUB REPO OLUŞTUR (Eğer yoksa)

### Opsiyonel A: GitHub Desktop ile
```
1. GitHub Desktop aç
2. File > Add Local Repository
3. C:\Users\90505\yokdil_health_app seç
4. "Publish repository" tıkla
5. Repository name: yokdil-health-app
6. ✅ Public veya Private seç
```

### Opsiyonel B: Git CLI ile
```powershell
cd C:\Users\90505\yokdil_health_app

# Git init (eğer değilse)
git init
git add .
git commit -m "Initial commit: YÖKDİL Health App v2.0"

# GitHub'a push
# (GitHub'da önce repo oluştur: https://github.com/new)
git remote add origin https://github.com/KULLANICI_ADI/yokdil-health-app.git
git branch -M main
git push -u origin main
```

---

## 3️⃣ RAILWAY'DE DEPLOY ET

### A) PostgreSQL Ekle
1. Railway Dashboard > **"+ New"**
2. **"Database"** > **"PostgreSQL"**
3. Otomatik oluşturulur
4. **DATABASE_URL** otomatik oluşur

### B) Backend Deploy Et
1. Railway Dashboard > **"+ New"**
2. **"GitHub Repo"**
3. **yokdil-health-app** repo'yu seç
4. **Deploy** başlar

### C) Environment Variables Ayarla
Backend service'e tıkla > **"Variables"** sekmesi:

```env
# Otomatik eklenir (PostgreSQL'den):
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Manuel ekle:
SECRET_KEY=your-super-secret-production-key-min-32-chars-change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS (Railway domain'i ekle)
ALLOWED_ORIGINS=https://yokdil-health-app-production.up.railway.app,http://localhost:3000

# Environment
ENVIRONMENT=production
ENABLE_HSTS=true

# OpenAI (opsiyonel)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Redis (opsiyonel - Railway'de eklenebilir)
REDIS_URL=${{Redis.REDIS_URL}}

# MinIO (opsiyonel - başka serviste)
MINIO_ENDPOINT=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
MINIO_BUCKET_NAME=yokdil-pdfs
```

### D) Deploy Komutlarını Ayarla
Backend service > **"Settings"** > **"Deploy"**:

**Start Command:**
```bash
cd backend && alembic upgrade head && python scripts/seed_trap_types.py || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Healthcheck Path:**
```
/health
```

---

## 4️⃣ TEST ET

### Deploy Tamamlandı mı?
Railway Dashboard'da **"Deployments"** sekmesine bak:
- ✅ **"Success"** görmelisin
- 🔗 **Domain** linki görünür

### API'yi Test Et

**1. Health Check:**
```
https://yokdil-health-app-production.up.railway.app/health
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

**2. API Docs (Development'ta aktif):**
```
https://yokdil-health-app-production.up.railway.app/docs
```
(Production'da kapalı, `ENVIRONMENT=development` yaparsanız açılır)

**3. İlk Kullanıcı Oluştur:**
```bash
curl -X POST https://yokdil-health-app-production.up.railway.app/api/v1/auth/register \
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

## 5️⃣ REDIS EKLE (Opsiyonel)

Railway Dashboard > **"+ New"** > **"Database"** > **"Redis"**

Sonra Backend Variables'a ekle:
```env
REDIS_URL=${{Redis.REDIS_URL}}
```

---

## 🎯 RAILWAY ÜCRETSİZ LİMİTLER

- ✅ **$5/ay ücretsiz kredi**
- ✅ **PostgreSQL** (100 MB)
- ✅ **Redis** (25 MB)
- ✅ **500 saat çalışma/ay**
- ✅ **Otomatik HTTPS**
- ✅ **Custom domain** desteği

---

## 🆘 SORUN GİDERME

### Build Hatası
```
Railway Dashboard > Backend > Deployments > Log'lara bak
```

**Sık Hatalar:**
1. **Requirements yüklenemiyor:**
   - `nixpacks.toml` var mı kontrol et
   
2. **Migration hatası:**
   - Environment variables doğru mu?
   - DATABASE_URL set edilmiş mi?

3. **Port hatası:**
   - Railway otomatik `$PORT` variable'ı verir
   - `uvicorn --port $PORT` kullan

### Migration Manuel Çalıştır
Railway Dashboard > Backend > **"Shell"** sekmesi:
```bash
cd backend
alembic upgrade head
python scripts/seed_trap_types.py
```

### Logs İzle
Railway Dashboard > Backend > **"Logs"** sekmesi:
- Real-time logs görürsün
- Hata ayıklama için kullan

---

## 📱 FLUTTER WEB DEPLOY (Bonus)

### 1. Flutter Web Build
```powershell
cd C:\Users\90505\yokdil_health_app\flutter_app

# Build
flutter build web --release

# Output: build/web/
```

### 2. Vercel/Netlify'a Deploy
```
1. build/web/ klasörünü zip'le
2. Vercel.com'a git
3. "New Project" > "Import" > zip'i yükle
4. Deploy!
```

**Veya Railway'e:**
```
Railway > + New > Deploy from GitHub
flutter_app/ klasörünü seç
Build Command: flutter build web
Start Command: python -m http.server 8080 --directory build/web
```

---

## ✅ BAŞARILI DEPLOY KONTROLÜ

- ✅ `https://your-app.railway.app/health` → 200 OK
- ✅ Backend logs'ta hata yok
- ✅ PostgreSQL bağlantısı çalışıyor
- ✅ Trap types seed edilmiş (logs'ta göreceksin)
- ✅ Register/Login test edildi

---

## 🎉 TAMAMLANDI!

```
╔════════════════════════════════════════════╗
║                                            ║
║   ✅ BACKEND WEB'DE ÇALIŞIYOR!            ║
║                                            ║
║   URL: https://your-app.railway.app       ║
║   Health: /health                         ║
║   API: /api/v1/                           ║
║                                            ║
║   • PostgreSQL ✅                         ║
║   • Auto-Deploy ✅                        ║
║   • HTTPS ✅                              ║
║   • 180+ Features ✅                      ║
║                                            ║
║   🚀 PROJE ONLINE!                        ║
║                                            ║
╚════════════════════════════════════════════╝
```

**Railway Dashboard:** https://railway.app/dashboard

**Süre:** ~5 dakika
**Maliyet:** Ücretsiz ($5/ay kredi)
