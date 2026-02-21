# YÖKDİL Health App - Backend Başlatma Scripti
# PowerShell Script

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "YÖKDİL HEALTH APP - Backend Başlatma" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Proje dizinine git
Set-Location "$PSScriptRoot\backend"

Write-Host "[1/6] Ortam kontrolü..." -ForegroundColor Yellow

# Python kontrolü
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ HATA: Python bulunamadı!" -ForegroundColor Red
    Write-Host "Python 3.11+ yükleyin: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version
Write-Host "✅ Python bulundu: $pythonVersion" -ForegroundColor Green

# PostgreSQL kontrolü
Write-Host "`n[2/6] PostgreSQL kontrolü..." -ForegroundColor Yellow
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService) {
        if ($pgService.Status -ne "Running") {
            Write-Host "⚠️  PostgreSQL servisi durmuş, başlatılıyor..." -ForegroundColor Yellow
            Start-Service $pgService.Name
        }
        Write-Host "✅ PostgreSQL çalışıyor" -ForegroundColor Green
    } else {
        Write-Host "⚠️  PostgreSQL servisi bulunamadı (Docker kullanıyor olabilirsiniz)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  PostgreSQL kontrolü atlandi" -ForegroundColor Yellow
}

# Redis kontrolü
Write-Host "`n[3/6] Redis kontrolü..." -ForegroundColor Yellow
try {
    $redisService = Get-Service -Name "Memurai*","Redis*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($redisService) {
        if ($redisService.Status -ne "Running") {
            Write-Host "⚠️  Redis/Memurai servisi durmuş, başlatılıyor..." -ForegroundColor Yellow
            Start-Service $redisService.Name
        }
        Write-Host "✅ Redis/Memurai çalışıyor" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Redis servisi bulunamadı" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Redis kontrolü atlandı" -ForegroundColor Yellow
}

# Virtual environment kontrolü
Write-Host "`n[4/6] Virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment bulunamadı, oluşturuluyor..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment oluşturuldu" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment mevcut" -ForegroundColor Green
}

# Activate venv
Write-Host "Virtual environment aktif ediliyor..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Dependencies
Write-Host "`n[5/6] Dependencies kontrol..." -ForegroundColor Yellow
$requirementsHash = Get-FileHash "requirements.txt" -Algorithm MD5
$installedHash = $null
if (Test-Path ".requirements.hash") {
    $installedHash = Get-Content ".requirements.hash"
}

if ($requirementsHash.Hash -ne $installedHash) {
    Write-Host "Yeni dependencies tespit edildi, yükleniyor..." -ForegroundColor Yellow
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    $requirementsHash.Hash | Out-File ".requirements.hash"
    Write-Host "✅ Dependencies yüklendi" -ForegroundColor Green
} else {
    Write-Host "✅ Dependencies güncel" -ForegroundColor Green
}

# .env kontrolü
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env dosyası bulunamadı!" -ForegroundColor Red
    Write-Host ".env.example dosyasını .env olarak kopyalayıp düzenleyin" -ForegroundColor Red
    exit 1
}

# Database migration
Write-Host "`n[6/6] Database migration..." -ForegroundColor Yellow
try {
    alembic current 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Migration gerekli, çalıştırılıyor..." -ForegroundColor Yellow
        alembic upgrade head
    }
    Write-Host "✅ Database güncel" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Migration kontrolü atlandı" -ForegroundColor Yellow
}

# Trap types seed kontrolü
Write-Host "`n[BONUS] Trap types seed kontrolü..." -ForegroundColor Yellow
Write-Host "Not: İlk kurulumda 'python scripts\seed_trap_types.py' çalıştırın" -ForegroundColor Gray

# Backend başlat
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "✅ TÜM KONTROLLER TAMAMLANDI!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend başlatılıyor..." -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Durdurmak için CTRL+C" -ForegroundColor Gray
Write-Host ""

# Uvicorn başlat
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
