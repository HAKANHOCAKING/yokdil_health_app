# 🚀 GIT CLI İLE HIZLI YÜKLEME (5 Dakika)

## ADIM 1: GIT KURU (2 dk)

1. **İndir:**
   ```
   https://git-scm.com/download/win
   ```

2. **Yükle:**
   - "Click here to download" tıkla
   - İndirilen .exe'yi çalıştır
   - Tüm ayarlar default (Next, Next, Next)
   - "Install" tıkla

3. **Doğrula:**
   ```powershell
   # PowerShell'i KAPAT ve YENİDEN AÇ (önemli!)
   git --version
   # git version 2.43.0 gibi bir şey görmelisin
   ```

✅ Git kuruldu!

---

## ADIM 2: GIT YAPILANDIRMASI (1 dk)

```powershell
# GitHub kullanıcı adın ve email'in
git config --global user.name "GITHUB_KULLANICI_ADIN"
git config --global user.email "github_emailin@example.com"

# Kontrol et
git config --global user.name
git config --global user.email
```

✅ Git yapılandırıldı!

---

## ADIM 3: PROJE KLASÖRÜNDE GIT BAŞLAT (2 dk)

```powershell
# Proje dizinine git
cd C:\Users\90505\yokdil_health_app

# Git başlat
git init

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: YÖKDİL Health App v2.0 - Enterprise Security + 20 Trap Types"
```

✅ Git repository oluşturuldu!

---

## ADIM 4: GITHUB'DA REPOSITORY OLUŞTUR (1 dk)

1. **GitHub'a Git:**
   ```
   https://github.com/new
   ```

2. **Repository Ayarları:**
   ```
   Repository name: yokdil-health-app
   Description: YÖKDİL Health App - Enterprise Edition
   ○ Public  ⦿ Private (seç)
   
   ☐ Add a README file (boş bırak, bizde var)
   ☐ Add .gitignore (boş bırak, bizde var)
   ☐ Choose a license (boş bırak)
   
   "Create repository" butonu
   ```

3. **GitHub Sayfası Açılır:**
   ```
   ...or push an existing repository from the command line
   
   Bu komutları kopyala:
   ```

✅ GitHub'da repo oluşturuldu!

---

## ADIM 5: GITHUB'A PUSH ET (1 dk)

GitHub'ın verdiği komutları çalıştır:

```powershell
# Remote ekle (GitHub'daki URL)
git remote add origin https://github.com/KULLANICI_ADI/yokdil-health-app.git

# Branch adını main yap
git branch -M main

# GitHub'a push et
git push -u origin main
```

**NOT:** GitHub şifre isterse:
- Personal Access Token kullanmalısın
- Veya GitHub Desktop kullan (daha kolay!)

✅ GitHub'a yüklendi!

---

## ADIM 6: KONTROL ET

Browser'da:
```
https://github.com/KULLANICI_ADI/yokdil-health-app
```

Tüm dosyaları göreceksin!

✅ Proje GitHub'da!

---

## 🔐 GITHUB AUTH (Şifre İsterse)

Git CLI şifre istiyorsa 2 seçenek:

### Opsiyonel A: Personal Access Token (Güvenli)

1. **GitHub'da Token Oluştur:**
   ```
   GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   → Generate new token (classic)
   
   Note: Railway Deploy Token
   Expiration: 90 days
   Scopes: ✅ repo (tüm kutucukları işaretle)
   
   "Generate token" butonu
   Token'ı KOPYALA (bir daha göremezsin!)
   ```

2. **Push Yaparken:**
   ```
   Username: GITHUB_KULLANICI_ADIN
   Password: [TOKEN'I YAPIŞTIR]
   ```

### Opsiyonel B: GitHub Desktop Kullan (Kolay)

Git CLI sorunlu olursa GitHub Desktop kullan!

---

## 🔄 SONRADAN GÜNCELLEMELER

```powershell
cd C:\Users\90505\yokdil_health_app

# Değişiklikleri gör
git status

# Tüm değişiklikleri ekle
git add .

# Commit yap
git commit -m "Update: [değişiklik açıklaması]"

# GitHub'a push et
git push

# Railway otomatik deploy eder!
```

---

## ✅ BAŞARILAR!

Git'i kur → Yapılandır → Push et → Railway'e geç!

**Toplam Süre:** 5-8 dakika

**Sorun çıkarsa:** GitHub Desktop kullan (daha kolay!)
