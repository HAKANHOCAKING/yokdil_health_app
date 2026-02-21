# 🚂 RAILWAY.APP İLE DEPLOY - ADIM ADIM DETAYLI REHBER

## 📋 ÖN HAZIRLIK (2 Dakika)

### ✅ Gereksinimler
1. ✅ GitHub hesabı (varsa tamam, yoksa ücretsiz oluştur)
2. ✅ Proje kodu hazır (bizde hazır!)
3. ✅ Railway hesabı (şimdi oluşturacağız)

---

## 🎯 ADIM 1: GITHUB'A PROJE YÜKLEYELİM (5 Dakika)

### Opsiyonel A: GitHub Desktop ile (KOLAY)

**1. GitHub Desktop İndir ve Kur:**
```
https://desktop.github.com/
İndir → Yükle → GitHub ile giriş yap
```

**2. Proje Klasörünü Ekle:**
```
1. GitHub Desktop aç
2. File → Add Local Repository
3. C:\Users\90505\yokdil_health_app seç
4. "Create a repository" butonu çıkarsa tıkla
5. Name: yokdil-health-app
6. Description: YÖKDİL Health App - Enterprise API
7. ✅ Initialize this repository with a README (boş bırak, bizde var)
8. "Create Repository" tıkla
```

**3. GitHub'a Yükle (Publish):**
```
1. GitHub Desktop'ta "Publish repository" butonu
2. Name: yokdil-health-app
3. Description: (otomatik dolu)
4. ☐ Keep this code private (işaretle veya bırak)
5. "Publish Repository" butonu
6. ✅ TAMAM! GitHub'da repo oluştu
```

**GitHub URL'in:** `https://github.com/KULLANICI_ADI/yokdil-health-app`

---

### Opsiyonel B: Git CLI ile (Terminal)

```powershell
# 1. Proje dizinine git
cd C:\Users\90505\yokdil_health_app

# 2. Git init (eğer değilse)
git init
git add .
git commit -m "Initial commit: YÖKDİL Health App v2.0 - Enterprise Edition"

# 3. GitHub'da repo oluştur
# https://github.com/new adresine git
# Repository name: yokdil-health-app
# "Create repository" tıkla

# 4. GitHub'a push
git remote add origin https://github.com/KULLANICI_ADI/yokdil-health-app.git
git branch -M main
git push -u origin main
```

---

## 🚀 ADIM 2: RAILWAY HESABI OLUŞTUR (1 Dakika)

**1. Railway.app'e Git:**
```
https://railway.app/
```

**2. Sign Up:**
```
1. "Login" butonu (sağ üstte)
2. "Login with GitHub" seç
3. GitHub authorization → "Authorize Railway" tıkla
4. ✅ Railway Dashboard açılır
```

**İLK GİRİŞ BONUSU:**
- 🎁 $5 ücretsiz kredi
- ✅ Kredi kartı gerektirmez
- ✅ 500+ saat ücretsiz compute

---

## 🗄️ ADIM 3: POSTGRESQL EKLE (2 Dakika)

**1. Dashboard'da "New Project":**
```
1. Railway Dashboard ana sayfa
2. Sağ üstte "+ New Project" butonu
3. "Provision PostgreSQL" seç
```

**2. PostgreSQL Otomatik Oluşur:**
```
✅ PostgreSQL instance oluştu
✅ Otomatik database oluşturuldu
✅ Connection string hazır
```

**3. PostgreSQL Ayarları Gör:**
```
1. PostgreSQL kartına tıkla
2. "Variables" sekmesi
3. DATABASE_URL göreceksin (otomatik)
```

**NOT:** Bu DATABASE_URL'i backend'e bağlayacağız.

---

## 🔧 ADIM 4: BACKEND SERVİSİ EKLE (3 Dakika)

**1. Aynı Project'e Backend Ekle:**
```
1. Sol üstte project adına tıkla (geri dön)
2. "+ New" butonu (sağ üstte)
3. "GitHub Repo" seç
4. "Configure GitHub App" (ilk seferse)
   → Repository access → "Only select repositories"
   → yokdil-health-app seç
   → "Install & Authorize"
5. Repo listesinde "yokdil-health-app" görünür → Seç
```

**2. Deploy Başlar (Otomatik):**
```
✅ Railway repo'yu clone eder
✅ Python ortamı kurar
✅ Dependencies yükler
✅ Deploy başlar

⏱️ İlk deploy 3-5 dakika sürer
```

**3. Deployment Status:**
```
1. Backend service kartına tıkla
2. "Deployments" sekmesi
3. Durum göreceksin:
   - 🟡 Building
   - 🟡 Deploying
   - 🟢 Success (başarılı)
   - 🔴 Failed (hata varsa)
```

---

## ⚙️ ADIM 5: ENVIRONMENT VARIABLES AYARLA (5 Dakika)

**1. Backend Service → Variables Sekmesi:**
```
1. Backend service kartına tıkla
2. "Variables" sekmesi
3. "New Variable" butonu
```

**2. PostgreSQL Bağlantısını Ekle:**
```
Variable Name: DATABASE_URL
Value: ${{Postgres.DATABASE_URL}}

(Railway otomatik PostgreSQL'i bağlar)

"Add" butonu
```

**3. Diğer Gerekli Variables:**

Her birini tek tek ekle:

```env
# JWT Secret (ÖNEMLİ: Kendin değiştir!)
SECRET_KEY=your-railway-super-secret-production-key-min-32-chars-change-this

# JWT Ayarları
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS (Railway domain'ini ekle)
ALLOWED_ORIGINS=https://yokdil-health-app-production.up.railway.app,http://localhost:3000

# Environment
ENVIRONMENT=production
ENABLE_HSTS=true
LOG_LEVEL=INFO

# Security
HSTS_MAX_AGE=31536000
MAX_UPLOAD_SIZE_MB=100

# Data Retention
AUDIT_LOG_RETENTION_DAYS=730
ATTEMPT_RETENTION_DAYS=365

# MFA (opsiyonel)
ENABLE_MFA=false

# OpenAI (opsiyonel - AI features için)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4-turbo-preview

# API Config
API_V1_PREFIX=/api/v1
PROJECT_NAME=YÖKDİL Health App
VERSION=2.0.0
```

**4. Redis Ekle (Opsiyonel):**
```
1. Project'e dön (sol üst)
2. "+ New" → "Redis"
3. Redis oluşur
4. Backend Variables'a ekle:
   REDIS_URL=${{Redis.REDIS_URL}}
```

**5. Variables Kaydet:**
```
Tüm variables eklendikten sonra Railway otomatik redeploy eder
```

---

## 🔨 ADIM 6: BUILD AYARLARI (2 Dakika)

**1. Backend Service → Settings:**
```
1. Backend service kartı
2. "Settings" sekmesi
3. Aşağı kaydır
```

**2. Root Directory:**
```
Root Directory: backend
(Proje backend/ klasöründe olduğu için)

"Update" butonu
```

**3. Build Command (Otomatik ama kontrol et):**
```
Build Command: pip install -r requirements.txt

(Railway otomatik tespit eder, dokunma)
```

**4. Start Command (ÖNEMLİ!):**
```
Start Command alanına şunu yaz:

alembic upgrade head && python scripts/seed_trap_types.py || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT

Bu komut sırayla:
1. Database migration çalıştırır
2. Trap types seed eder
3. Backend'i başlatır

"Update" butonu
```

**5. Healthcheck Path:**
```
Healthcheck Path: /health

(Railway bu endpoint'i kontrol eder)

"Update" butonu
```

---

## 🌐 ADIM 7: DOMAIN VE URL (1 Dakika)

**1. Public Domain Al:**
```
1. Backend service → Settings
2. "Networking" bölümü
3. "Generate Domain" butonu
4. ✅ Otomatik domain oluşur:
   https://yokdil-health-app-production.up.railway.app
```

**2. Custom Domain (Opsiyonel):**
```
Kendi domain'in varsa:
1. "Custom Domains" → "Add Domain"
2. api.yokdil-app.com
3. DNS ayarlarını yap (CNAME)
4. SSL otomatik oluşur
```

---

## ✅ ADIM 8: DEPLOY TAMAMLANDI - TEST ET! (2 Dakika)

**1. Deploy Durumu Kontrol:**
```
1. Backend service → "Deployments"
2. En son deployment:
   🟢 Success görmelisin
3. Logs'ta hata var mı bak
```

**2. Health Check Test:**

Browser'da aç veya PowerShell'de:

```powershell
# Browser
https://yokdil-health-app-production.up.railway.app/health

# PowerShell
curl https://yokdil-health-app-production.up.railway.app/health
```

**Beklenen Response:**
```json
{
  "status": "healthy",
  "service": "YÖKDİL Health App",
  "version": "2.0.0",
  "environment": "production"
}
```

**3. API Docs (Development'taysa):**
```
https://yokdil-health-app-production.up.railway.app/docs
```

**4. İlk Kullanıcı Oluştur:**

```powershell
curl -X POST https://yokdil-health-app-production.up.railway.app/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "demo@example.com",
    "password": "DemoPass123!",
    "full_name": "Demo User",
    "role": "student",
    "tenant_id": "00000000-0000-0000-0000-000000000001"
  }'
```

**Beklenen Response:**
```json
{
  "id": "...",
  "email": "demo@example.com",
  "full_name": "Demo User",
  "role": "student",
  ...
}
```

---

## 📊 ADIM 9: LOGS VE MONİTORİNG (1 Dakika)

**1. Real-time Logs:**
```
1. Backend service → "Logs" sekmesi
2. Real-time logs akışını gör
3. Hata varsa burada görünür
```

**2. Ne Görmelisin:**
```
✅ Alembic migration success
✅ Seeded 20 trap types
✅ Uvicorn running on port XXX
✅ Application startup complete
```

**3. Metrics:**
```
1. Backend service → "Metrics" sekmesi
2. CPU, Memory, Network kullanımı
3. Request count, response time
```

---

## 🔄 ADIM 10: AUTO-DEPLOY AYARLA (1 Dakika)

**Railway Otomatik Auto-Deploy Aktif!**

**Ne Demek?**
```
GitHub'a her push attığında:
1. Railway otomatik tespit eder
2. Yeni kod'u çeker
3. Build eder
4. Deploy eder
5. ✅ Site güncellenir

Hiçbir şey yapman gerekmez!
```

**Test Et:**
```powershell
# Lokal'de değişiklik yap
cd C:\Users\90505\yokdil_health_app
echo "# Update" >> README.md

# GitHub'a push et
git add .
git commit -m "Test auto-deploy"
git push

# Railway Dashboard'da:
→ Yeni deployment başlar (otomatik)
→ 2-3 dakika sonra online
```

---

## 🎯 SONRAKI ADIMLAR

### A) Demo Sayfasını Güncelle:
```
1. demo/index.html aç
2. API URL'i güncelle:
   const API_URL = 'https://yokdil-health-app-production.up.railway.app';
3. Browser'da aç ve test et!
```

### B) Celery Worker Ekle (Background Tasks):
```
1. Project → "+ New" → "Empty Service"
2. GitHub repo seç (aynı)
3. Root Directory: backend
4. Start Command:
   celery -A app.worker.celery_app worker -l info -Q pdf,ai,export
5. Environment Variables'ı kopyala (aynı)
6. Deploy!
```

### C) MinIO Ekle (PDF Storage):
```
Railway'de MinIO yok, alternatifler:
- AWS S3 (ücretsiz tier)
- Cloudflare R2 (ücretsiz 10GB)
- Render.com Disk (persistent disk)
```

---

## 💰 MALİYET VE LİMİTLER

### Ücretsiz Tier ($5/ay kredi):
```
✅ PostgreSQL (100 MB)
✅ Redis (25 MB) - opsiyonel
✅ Backend service (512 MB RAM)
✅ 500 saat compute/ay
✅ Otomatik HTTPS
✅ Custom domain

🔮 $5 ile yaklaşık 20-30 gün çalışır (always-on)
```

### Ne Zaman Ücretli Olur?
```
- $5 kredi bitince
- 500 saat compute aşılınca
- Daha fazla RAM gerekirse

💳 Ücretli: $5/ay'dan başlar
```

---

## 🆘 SORUN GİDERME

### Build Hatası
```
Logs'ta: "ERROR: Could not install packages"

Çözüm:
1. requirements.txt kontrol et
2. Python version (3.11) doğru mu?
3. Root Directory: backend mi?
```

### Migration Hatası
```
Logs'ta: "ERROR: relation 'users' does not exist"

Çözüm:
1. Backend service → "Shell" sekmesi (üstte)
2. Çalıştır:
   cd backend
   alembic upgrade head
   python scripts/seed_trap_types.py
```

### Environment Variables Yok
```
Logs'ta: "SECRET_KEY not set"

Çözüm:
1. Variables sekmesi → Tüm variables eklenmiş mi?
2. DATABASE_URL: ${{Postgres.DATABASE_URL}} mi?
3. Railway otomatik redeploy eder
```

### Port Hatası
```
Logs'ta: "Port already in use"

Çözüm:
Start Command'de --port $PORT kullanıldığından emin ol
Railway otomatik port atar
```

### Deploy Çok Yavaş
```
İlk deploy 5-10 dakika sürebilir (normal)
Sonraki deploylar 2-3 dakika
```

---

## ✅ BAŞARILI DEPLOY KONTROLLERİ

Aşağıdakileri kontrol et:

```
✅ Railway Dashboard'da "Success" yazıyor
✅ /health endpoint 200 OK dönüyor
✅ Logs'ta hata yok
✅ Trap types seeded (logs'ta "20" yazıyor)
✅ Register endpoint çalışıyor
✅ PostgreSQL bağlı
✅ Auto-deploy aktif
```

---

## 🎉 TAMAMLANDI!

```
╔════════════════════════════════════════════╗
║                                            ║
║   ✅ RAILWAY DEPLOY TAMAMLANDI!           ║
║                                            ║
║   URL: https://your-app.up.railway.app    ║
║   Dashboard: https://railway.app/project  ║
║                                            ║
║   • PostgreSQL ✅                         ║
║   • Backend Online ✅                     ║
║   • Auto-Deploy ✅                        ║
║   • HTTPS ✅                              ║
║   • 180+ Features Live ✅                 ║
║                                            ║
║   🚀 PROJE WEB'DE ÇALIŞIYOR!              ║
║                                            ║
╚════════════════════════════════════════════╝
```

---

## 📱 FLUTTER WEB DEPLOY (Bonus)

```bash
# 1. Flutter web build
cd flutter_app
flutter build web --release

# 2. Vercel'e deploy (hızlı)
1. https://vercel.com/ git
2. New Project
3. build/web/ klasörünü yükle
4. Deploy!

# Flutter'da API URL'i güncelle:
const API_URL = 'https://yokdil-health-app-production.up.railway.app';
```

---

## 📚 FAYDALI LİNKLER

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway Docs:** https://docs.railway.app/
- **GitHub Repo:** https://github.com/KULLANICI_ADI/yokdil-health-app
- **Demo Page:** demo/index.html

---

**Herhangi bir sorun olursa:**
1. Railway Dashboard → Backend → Logs
2. Hatayı kopyala
3. Google'da ara veya Railway Discord'a sor

**BAŞARILAR! 🚀**
