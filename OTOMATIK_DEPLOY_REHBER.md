# 🤖 OTOMATİK DEPLOY SCRIPTLERI

## 📋 3 OTOMATİK YÖNTEM

Projeyi GitHub'a yükleyip Railway'e deploy etmek için 3 otomatik script hazırladım:

---

## ⚡ YÖNTEM 1: YARÎ-OTOMATİK (ÖNERİLEN)

**Script:** `auto-deploy.ps1`

**Ne Yapar:**
- ✅ Git kontrolü
- ✅ Git yapılandırması
- ✅ Dosyaları commit eder
- ✅ GitHub'a push eder
- ⚠️ GitHub URL'ini senden ister
- ⚠️ GitHub auth gerektirir

**Kullanım:**
```powershell
cd C:\Users\90505\yokdil_health_app
.\auto-deploy.ps1
```

**Gereksinimler:**
- Git kurulu olmalı
- GitHub hesabı olmalı

**Süre:** 5 dakika

---

## 📦 YÖNTEM 2: MANUELZİP UPLOAD (GİT YOK İSE)

**Script:** `create-github-upload-package.ps1`

**Ne Yapar:**
- ✅ Projeyi ZIP'ler
- ✅ Masaüstüne kaydeder
- ✅ Gereksiz dosyaları atar
- ⚠️ GitHub web'den manuel upload

**Kullanım:**
```powershell
cd C:\Users\90505\yokdil_health_app
.\create-github-upload-package.ps1
```

**Sonra:**
1. Desktop'taki ZIP'i al
2. https://github.com/new git
3. Repository oluştur
4. "uploading an existing file" → ZIP yükle
5. Railway'e geç

**Gereksinimler:**
- Sadece browser
- Git gerektirmez!

**Süre:** 3 dakika

---

## 🚀 YÖNTEM 3: TAM OTOMATİK (İLERİ SEVİYE)

**Script:** `full-auto-deploy.ps1`

**Ne Yapar:**
- ✅ Railway CLI ile otomatik deploy
- ✅ PostgreSQL otomatik ekler
- ✅ Environment variables ayarlar
- ✅ Domain otomatik alır
- ✅ Browser'da açar

**Kullanım:**
```powershell
cd C:\Users\90505\yokdil_health_app
.\full-auto-deploy.ps1
```

**Gereksinimler:**
- Railway CLI kurulu olmalı:
  ```powershell
  npm install -g @railway/cli
  ```

**Süre:** 10 dakika (ilk kez), sonra 2 dakika

---

## 🎯 HANGİSİNİ KULLANAYIM?

| Durum | Önerilen Script |
|-------|----------------|
| **Git kurulu** | `auto-deploy.ps1` ⚡ |
| **Git yok** | `create-github-upload-package.ps1` 📦 |
| **Railway CLI var** | `full-auto-deploy.ps1` 🚀 |
| **Hızlı test** | `create-github-upload-package.ps1` 📦 |

---

## ⚡ HEMEN BAŞLA!

### Git Kuruluysa:
```powershell
cd C:\Users\90505\yokdil_health_app
.\auto-deploy.ps1
```

### Git Yoksa (EN KOLAY):
```powershell
cd C:\Users\90505\yokdil_health_app
.\create-github-upload-package.ps1
```

Sonra masaüstündeki ZIP'i GitHub'a yükle!

---

## 📝 DETAYLI ADIMLAR

### Yöntem 2 (Manuel ZIP - Önerilen):

1. **PowerShell aç:**
   ```powershell
   cd C:\Users\90505\yokdil_health_app
   .\create-github-upload-package.ps1
   ```

2. **ZIP oluştu (Desktop'ta):**
   ```
   yokdil-health-app-upload.zip
   ```

3. **GitHub'da repo oluştur:**
   - https://github.com/new
   - Name: yokdil-health-app
   - "Create repository"

4. **ZIP yükle:**
   - "uploading an existing file" linkine tıkla
   - ZIP'i sürükle
   - "Commit changes"

5. **Railway'e geç:**
   - https://railway.app/
   - Login with GitHub
   - RAILWAY_ADIM_ADIM.md takip et

---

## 🆘 SORUN GİDERME

### "execution policy" Hatası:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Git bulunamadı" Hatası:
```
→ create-github-upload-package.ps1 kullan (Git gerektirmez)
```

### "Railway CLI yok" Hatası:
```
→ auto-deploy.ps1 veya create-github-upload-package.ps1 kullan
```

---

## ✅ BAŞARILI DEPLOY KONTROLÜ

Deploy tamamlandıktan sonra:

```powershell
# Health check
curl https://your-app.railway.app/health

# Beklenen:
# {"status": "healthy", ...}
```

---

## 🎉 ÖZET

```
╔════════════════════════════════════════════╗
║                                            ║
║   🤖 3 OTOMATİK SCRIPT HAZIR!             ║
║                                            ║
║   ⚡ auto-deploy.ps1                      ║
║      (Git ile otomatik)                   ║
║                                            ║
║   📦 create-github-upload-package.ps1     ║
║      (ZIP + Manuel upload) ← ÖNERİLEN    ║
║                                            ║
║   🚀 full-auto-deploy.ps1                 ║
║      (Railway CLI ile tam otomatik)       ║
║                                            ║
║   ✅ Hepsi tek tıkla çalışır!             ║
║                                            ║
╚════════════════════════════════════════════╝
```

---

## 🚀 ŞİMDİ ÇALIŞTIR!

**EN KOLAY YÖNTEM (Git gerektirmez):**

```powershell
cd C:\Users\90505\yokdil_health_app
.\create-github-upload-package.ps1
```

Sonra masaüstündeki ZIP'i GitHub'a yükle!

---

**Hazırsan, bir script seç ve çalıştır!** 🎉
