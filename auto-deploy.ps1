# 🚀 Otomatik GitHub ve Railway Deploy
# Tek tıkla tüm işlemler!

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🤖 OTOMATIK DEPLOY BAŞLIYOR..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Proje dizini
$projectPath = "C:\Users\90505\yokdil_health_app"
Set-Location $projectPath

Write-Host "[1/5] Gereksinimleri kontrol ediyorum..." -ForegroundColor Yellow

# Git kontrolü
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "❌ Git kurulu değil!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Git kurmak için:" -ForegroundColor Yellow
    Write-Host "1. https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. İndir ve yükle" -ForegroundColor White
    Write-Host "3. PowerShell'i kapat/aç" -ForegroundColor White
    Write-Host "4. Bu scripti tekrar çalıştır" -ForegroundColor White
    Write-Host ""
    
    # GitHub CLI alternatifi
    $ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
    if (-not $ghInstalled) {
        Write-Host "💡 Alternatif: GitHub CLI (daha kolay)" -ForegroundColor Cyan
        Write-Host "winget install GitHub.cli" -ForegroundColor White
        Write-Host ""
    }
    
    # Manuel yükleme seçeneği
    Write-Host "📦 Veya Manuel Yükleme:" -ForegroundColor Cyan
    Write-Host ".\create-github-upload-package.ps1 çalıştır" -ForegroundColor White
    
    exit 1
}

Write-Host "✅ Git bulundu: $(git --version)" -ForegroundColor Green

# Git yapılandırması kontrolü
$gitUserName = git config --global user.name
$gitUserEmail = git config --global user.email

if (-not $gitUserName -or -not $gitUserEmail) {
    Write-Host ""
    Write-Host "⚙️ Git yapılandırması gerekli!" -ForegroundColor Yellow
    Write-Host ""
    
    $userName = Read-Host "GitHub kullanıcı adın"
    $userEmail = Read-Host "GitHub email adresin"
    
    git config --global user.name $userName
    git config --global user.email $userEmail
    
    Write-Host "✅ Git yapılandırıldı" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] Git repository başlatılıyor..." -ForegroundColor Yellow

# Git repo kontrolü
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git repository oluşturuldu" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository mevcut" -ForegroundColor Green
}

# .gitignore kontrolü
if (-not (Test-Path ".gitignore")) {
    Write-Host "⚠️ .gitignore eksik, zaten oluşturulmuş olmalı" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] Dosyalar commit ediliyor..." -ForegroundColor Yellow

# Dosyaları ekle
git add .

# Commit mesajı
$commitMessage = "Initial commit: YÖKDİL Health App v2.0 - Enterprise Security + 20 Trap Types + 180+ Features"

# Commit yap
try {
    git commit -m $commitMessage
    Write-Host "✅ Commit oluşturuldu" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Commit zaten yapılmış veya değişiklik yok" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] GitHub repository bilgileri..." -ForegroundColor Yellow
Write-Host ""
Write-Host "GitHub'da repository oluşturman gerekiyor:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. https://github.com/new adresine git" -ForegroundColor White
Write-Host "2. Repository name: yokdil-health-app" -ForegroundColor White
Write-Host "3. 'Create repository' tıkla" -ForegroundColor White
Write-Host ""

# GitHub URL al
$repoUrl = Read-Host "GitHub repository URL'ini yapıştır (https://github.com/KULLANICI/yokdil-health-app.git)"

if ($repoUrl) {
    Write-Host ""
    Write-Host "[5/5] GitHub'a push ediliyor..." -ForegroundColor Yellow
    
    # Remote kontrolü
    $existingRemote = git remote get-url origin 2>$null
    
    if ($existingRemote) {
        Write-Host "Remote zaten mevcut, güncelleniyor..." -ForegroundColor Yellow
        git remote set-url origin $repoUrl
    } else {
        git remote add origin $repoUrl
    }
    
    # Branch
    git branch -M main
    
    # Push
    Write-Host ""
    Write-Host "GitHub'a push ediliyor..." -ForegroundColor Yellow
    Write-Host "(GitHub şifre/token isteyebilir)" -ForegroundColor Gray
    Write-Host ""
    
    try {
        git push -u origin main
        Write-Host ""
        Write-Host "✅ GitHub'a yüklendi!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
        
        # Railway bilgisi
        Write-Host ""
        Write-Host "=====================================" -ForegroundColor Cyan
        Write-Host "🚂 ŞİMDİ RAILWAY'E GEÇELİM!" -ForegroundColor Cyan
        Write-Host "=====================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. https://railway.app/ git" -ForegroundColor White
        Write-Host "2. 'Login with GitHub' tıkla" -ForegroundColor White
        Write-Host "3. '+ New Project' → 'Provision PostgreSQL'" -ForegroundColor White
        Write-Host "4. '+ New' → 'GitHub Repo' → 'yokdil-health-app' seç" -ForegroundColor White
        Write-Host ""
        Write-Host "Detaylı adımlar: RAILWAY_ADIM_ADIM.md" -ForegroundColor Cyan
        Write-Host ""
        
        # Railway CLI kontrolü
        $railwayInstalled = Get-Command railway -ErrorAction SilentlyContinue
        if ($railwayInstalled) {
            Write-Host "💡 Railway CLI bulundu! Otomatik deploy için:" -ForegroundColor Yellow
            Write-Host "railway login" -ForegroundColor White
            Write-Host "railway up" -ForegroundColor White
        } else {
            Write-Host "💡 Railway CLI kurarak otomatik deploy yapabilirsin:" -ForegroundColor Yellow
            Write-Host "npm install -g @railway/cli" -ForegroundColor White
        }
        
    } catch {
        Write-Host ""
        Write-Host "❌ Push hatası!" -ForegroundColor Red
        Write-Host "Muhtemelen authentication gerekiyor." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Çözüm 1: GitHub Desktop kullan (kolay)" -ForegroundColor Cyan
        Write-Host "  https://desktop.github.com/" -ForegroundColor White
        Write-Host ""
        Write-Host "Çözüm 2: Personal Access Token oluştur" -ForegroundColor Cyan
        Write-Host "  https://github.com/settings/tokens" -ForegroundColor White
        Write-Host ""
    }
} else {
    Write-Host ""
    Write-Host "❌ Repository URL girilmedi!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manuel olarak devam etmek için:" -ForegroundColor Yellow
    Write-Host "1. GitHub'da repository oluştur" -ForegroundColor White
    Write-Host "2. Bu scripti tekrar çalıştır" -ForegroundColor White
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Script tamamlandı!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
