# 🚀 TAM OTOMATİK DEPLOY (Railway CLI ile)
# Railway CLI kuruluysa tüm işlem otomatik!

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🚀 TAM OTOMATİK DEPLOY" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "C:\Users\90505\yokdil_health_app"
Set-Location $projectPath

# Railway CLI kontrolü
Write-Host "[1/6] Railway CLI kontrol ediliyor..." -ForegroundColor Yellow

$railwayInstalled = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayInstalled) {
    Write-Host "❌ Railway CLI kurulu değil!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Railway CLI kurulumu:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Yöntem 1 - NPM (Node.js gerekliyse):" -ForegroundColor Cyan
    Write-Host "  npm install -g @railway/cli" -ForegroundColor White
    Write-Host ""
    Write-Host "Yöntem 2 - Scoop (Windows):" -ForegroundColor Cyan
    Write-Host "  scoop install railway" -ForegroundColor White
    Write-Host ""
    Write-Host "Yöntem 3 - Direct Download:" -ForegroundColor Cyan
    Write-Host "  https://docs.railway.app/develop/cli" -ForegroundColor White
    Write-Host ""
    Write-Host "Kurulum sonrası bu scripti tekrar çalıştır" -ForegroundColor Yellow
    Write-Host ""
    
    exit 1
}

Write-Host "✅ Railway CLI bulundu" -ForegroundColor Green

Write-Host ""
Write-Host "[2/6] Railway'e giriş yapılıyor..." -ForegroundColor Yellow

# Railway login kontrolü
$loginCheck = railway whoami 2>&1

if ($loginCheck -like "*not logged in*" -or $LASTEXITCODE -ne 0) {
    Write-Host "Railway'e giriş yapman gerekiyor..." -ForegroundColor Yellow
    Write-Host "Browser açılacak, GitHub ile giriş yap" -ForegroundColor Gray
    Write-Host ""
    
    railway login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Giriş başarısız!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Railway girişi yapıldı" -ForegroundColor Green

Write-Host ""
Write-Host "[3/6] Railway project oluşturuluyor..." -ForegroundColor Yellow

# Project kontrolü
if (-not (Test-Path ".railway")) {
    # Yeni project
    railway init
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Project oluşturulamadı!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Project oluşturuldu" -ForegroundColor Green
} else {
    Write-Host "✅ Project mevcut" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/6] PostgreSQL ekleniyor..." -ForegroundColor Yellow

# PostgreSQL ekle
railway add --database postgres

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PostgreSQL eklendi" -ForegroundColor Green
} else {
    Write-Host "⚠️ PostgreSQL zaten mevcut olabilir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/6] Environment variables ayarlanıyor..." -ForegroundColor Yellow

# Environment variables
$envVars = @{
    "SECRET_KEY" = "railway-production-secret-key-min-32-chars-$(Get-Random -Minimum 1000 -Maximum 9999)"
    "ALGORITHM" = "HS256"
    "ACCESS_TOKEN_EXPIRE_MINUTES" = "15"
    "REFRESH_TOKEN_EXPIRE_DAYS" = "30"
    "ENVIRONMENT" = "production"
    "ENABLE_HSTS" = "true"
    "LOG_LEVEL" = "INFO"
    "API_V1_PREFIX" = "/api/v1"
    "PROJECT_NAME" = "YÖKDİL Health App"
    "VERSION" = "2.0.0"
}

foreach ($key in $envVars.Keys) {
    $value = $envVars[$key]
    Write-Host "Setting $key..." -ForegroundColor Gray
    railway variables set $key=$value
}

Write-Host "✅ Environment variables ayarlandı" -ForegroundColor Green

Write-Host ""
Write-Host "[6/6] Deploy ediliyor..." -ForegroundColor Yellow
Write-Host "Bu işlem 5-10 dakika sürebilir..." -ForegroundColor Gray
Write-Host ""

# Deploy
railway up

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "✅ DEPLOY BAŞARILI!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    
    # URL al
    Write-Host "URL alınıyor..." -ForegroundColor Gray
    $domain = railway domain
    
    if ($domain) {
        Write-Host ""
        Write-Host "🌐 Backend URL: https://$domain" -ForegroundColor Cyan
        Write-Host "🏥 Health Check: https://$domain/health" -ForegroundColor Cyan
        Write-Host "📚 API Docs: https://$domain/docs" -ForegroundColor Cyan
        Write-Host ""
        
        # Browser'da aç
        Write-Host "Health check açılıyor..." -ForegroundColor Gray
        Start-Process "https://$domain/health"
    }
    
    # Dashboard
    Write-Host ""
    Write-Host "📊 Railway Dashboard:" -ForegroundColor Yellow
    Write-Host "https://railway.app/dashboard" -ForegroundColor Cyan
    Write-Host ""
    
} else {
    Write-Host ""
    Write-Host "❌ Deploy başarısız!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Logs kontrol et:" -ForegroundColor Yellow
    Write-Host "railway logs" -ForegroundColor White
    Write-Host ""
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Script tamamlandı!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
