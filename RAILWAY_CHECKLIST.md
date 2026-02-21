# ✅ RAILWAY DEPLOY - HIZLI CHECKLIST

## 📋 TAKİP LİSTESİ

Aşağıdaki adımları sırayla işaretle:

---

### 🔧 ÖN HAZIRLIK

- [ ] **GitHub hesabım var** (yoksa: https://github.com/join)
- [ ] **Proje kodları hazır** (C:\Users\90505\yokdil_health_app)
- [ ] **Internet bağlantım stabil**

---

### 📦 ADIM 1: GITHUB'A YÜKLEYeceğim

#### Opsiyonel A: GitHub Desktop (Kolay)
- [ ] GitHub Desktop indirdim: https://desktop.github.com/
- [ ] GitHub Desktop açtım ve giriş yaptım
- [ ] File → Add Local Repository
- [ ] `C:\Users\90505\yokdil_health_app` seçtim
- [ ] "Publish repository" tıkladım
- [ ] Repo adı: `yokdil-health-app`
- [ ] ✅ GitHub'da repo oluştu

#### Opsiyonel B: Git CLI (Terminal)
- [ ] Git yüklü (test: `git --version`)
- [ ] Proje dizininde: `git init`
- [ ] `git add .` çalıştırdım
- [ ] `git commit -m "Initial commit"` yaptım
- [ ] GitHub'da repo oluşturdum: https://github.com/new
- [ ] `git remote add origin ...` çalıştırdım
- [ ] `git push -u origin main` yaptım
- [ ] ✅ GitHub'da kod görünüyor

**GitHub URL'im:** `https://github.com/___________/yokdil-health-app`

---

### 🚂 ADIM 2: RAILWAY HESABI

- [ ] https://railway.app/ gittim
- [ ] "Login" butonuna tıkladım
- [ ] "Login with GitHub" seçtim
- [ ] GitHub authorization onayladım
- [ ] ✅ Railway Dashboard açıldı

---

### 🗄️ ADIM 3: POSTGRESQL EKLEDİM

- [ ] Railway Dashboard'da "+ New Project"
- [ ] "Provision PostgreSQL" seçtim
- [ ] ✅ PostgreSQL oluştu
- [ ] PostgreSQL kartına tıkladım
- [ ] "Variables" sekmesinde DATABASE_URL gördüm

---

### 🔧 ADIM 4: BACKEND SERVİSİ EKLEDİM

- [ ] Project'e geri döndüm
- [ ] "+ New" → "GitHub Repo"
- [ ] "Configure GitHub App" (ilk seferse)
- [ ] `yokdil-health-app` repo'yu seçtim
- [ ] Deploy başladı
- [ ] ✅ "Building" yazıyor

---

### ⚙️ ADIM 5: ENVIRONMENT VARIABLES

Backend service → "Variables" sekmesi:

- [ ] `DATABASE_URL = ${{Postgres.DATABASE_URL}}`
- [ ] `SECRET_KEY = ` (kendi secret key'imi yazdım)
- [ ] `ALGORITHM = HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES = 15`
- [ ] `REFRESH_TOKEN_EXPIRE_DAYS = 30`
- [ ] `ALLOWED_ORIGINS = ` (Railway domain)
- [ ] `ENVIRONMENT = production`
- [ ] `ENABLE_HSTS = true`
- [ ] `LOG_LEVEL = INFO`
- [ ] `API_V1_PREFIX = /api/v1`
- [ ] `PROJECT_NAME = YÖKDİL Health App`
- [ ] `VERSION = 2.0.0`
- [ ] ✅ Tüm variables eklendi

---

### 🔨 ADIM 6: BUILD AYARLARI

Backend service → "Settings" sekmesi:

- [ ] **Root Directory:** `backend` yazdım
- [ ] **Start Command:** 
  ```
  alembic upgrade head && python scripts/seed_trap_types.py || true && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] **Healthcheck Path:** `/health` yazdım
- [ ] "Update" butonuna tıkladım
- [ ] ✅ Redeploy başladı

---

### 🌐 ADIM 7: DOMAIN

Backend service → "Settings" → "Networking":

- [ ] "Generate Domain" tıkladım
- [ ] ✅ Domain oluştu
- [ ] Domain URL'imi not aldım: `___________________.up.railway.app`

---

### ✅ ADIM 8: TEST ETTİM

- [ ] Backend → "Deployments" sekmesi
- [ ] 🟢 "Success" yazıyor
- [ ] "Logs" sekmesinde hata yok
- [ ] Logs'ta "Seeded 20 trap types" gördüm

**Health Check Test:**
```
Browser'da açtım: https://[DOMAIN]/health
```

- [ ] ✅ `{"status": "healthy", ...}` döndü

**İlk Kullanıcı:**
```powershell
curl -X POST https://[DOMAIN]/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "role": "student",
    "tenant_id": "00000000-0000-0000-0000-000000000001"
  }'
```

- [ ] ✅ User oluşturuldu

---

### 📊 ADIM 9: MONİTORİNG

- [ ] Backend → "Logs" sekmesini kontrol ettim
- [ ] Backend → "Metrics" sekmesini kontrol ettim
- [ ] CPU, Memory kullanımı normal

---

### 🔄 ADIM 10: AUTO-DEPLOY

- [ ] Railway otomatik auto-deploy aktif (default)
- [ ] Test için: Lokal'de değişiklik yaptım
- [ ] GitHub'a push attım
- [ ] Railway otomatik deploy etti
- [ ] ✅ Auto-deploy çalışıyor

---

## 🎉 TAMAMLANDI!

### Final Checklist:

- [ ] ✅ Backend online ve çalışıyor
- [ ] ✅ PostgreSQL bağlı
- [ ] ✅ `/health` endpoint 200 OK
- [ ] ✅ Trap types seeded (20)
- [ ] ✅ Register endpoint çalışıyor
- [ ] ✅ Auto-deploy aktif
- [ ] ✅ Domain URL'im var
- [ ] ✅ Logs'ta hata yok

---

## 📝 ÖNEMLİ BİLGİLER (KAYDET!)

**GitHub Repo:**
```
https://github.com/__________/yokdil-health-app
```

**Railway Project:**
```
https://railway.app/project/__________
```

**Backend URL:**
```
https://__________________.up.railway.app
```

**Health Check:**
```
https://__________________.up.railway.app/health
```

**API Docs (dev):**
```
https://__________________.up.railway.app/docs
```

---

## 🆘 SORUN OLURSA

1. **Build hatası:**
   - Logs sekmesine bak
   - Root Directory "backend" mi?
   - Variables eksiksiz mi?

2. **Database hatası:**
   - DATABASE_URL: `${{Postgres.DATABASE_URL}}` mi?
   - PostgreSQL servisi çalışıyor mu?

3. **Migration hatası:**
   - Shell sekmesinden manuel çalıştır:
     ```
     cd backend
     alembic upgrade head
     python scripts/seed_trap_types.py
     ```

4. **Genel sorun:**
   - Railway Dashboard → Backend → Logs
   - Hatayı oku ve Google'da ara
   - Railway Discord'a sor

---

## 📚 YARDIMCI KAYNAKLAR

- **Detaylı Rehber:** `RAILWAY_ADIM_ADIM.md`
- **Railway Docs:** https://docs.railway.app/
- **Demo Page:** `demo/index.html`
- **Proje Özeti:** `FINAL_IMPLEMENTATION_SUMMARY.md`

---

**BAŞARILAR! 🚀**

Tüm checkboxlar işaretli mi? TAMAMLANDIN! 🎉
