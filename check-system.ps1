# YÖKDİL Health App - Sistem Kontrol Scripti
# Tüm gereksinimleri kontrol eder

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "YÖKDİL HEALTH APP - Sistem Kontrol" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# Python
Write-Host "[1/8] Python..." -NoNewline
if (Get-Command python -ErrorAction SilentlyContinue) {
    $version = python --version
    Write-Host " ✅ $version" -ForegroundColor Green
} else {
    Write-Host " ❌ Bulunamadı" -ForegroundColor Red
    Write-Host "      Yükle: https://www.python.org/downloads/" -ForegroundColor Yellow
    $allOk = $false
}

# PostgreSQL
Write-Host "[2/8] PostgreSQL..." -NoNewline
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pgService) {
        if ($pgService.Status -eq "Running") {
            Write-Host " ✅ Çalışıyor" -ForegroundColor Green
        } else {
            Write-Host " ⚠️  Durmuş (başlatılabilir)" -ForegroundColor Yellow
        }
    } else {
        Write-Host " ⚠️  Servis bulunamadı (Docker?)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Kontrol edilemedi" -ForegroundColor Yellow
}

# Redis
Write-Host "[3/8] Redis/Memurai..." -NoNewline
try {
    $redisService = Get-Service -Name "Memurai*","Redis*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($redisService) {
        if ($redisService.Status -eq "Running") {
            Write-Host " ✅ Çalışıyor" -ForegroundColor Green
        } else {
            Write-Host " ⚠️  Durmuş (başlatılabilir)" -ForegroundColor Yellow
        }
    } else {
        Write-Host " ⚠️  Bulunamadı" -ForegroundColor Yellow
        Write-Host "      Yükle: https://www.memurai.com/get-memurai" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Kontrol edilemedi" -ForegroundColor Yellow
}

# Docker (Opsiyonel)
Write-Host "[4/8] Docker..." -NoNewline
if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
        $version = docker --version
        Write-Host " ✅ $version" -ForegroundColor Green
    } catch {
        Write-Host " ⚠️  Yüklü ama çalışmıyor" -ForegroundColor Yellow
    }
} else {
    Write-Host " ⚠️  Bulunamadı (opsiyonel)" -ForegroundColor Gray
}

# Flutter (Opsiyonel)
Write-Host "[5/8] Flutter..." -NoNewline
if (Get-Command flutter -ErrorAction SilentlyContinue) {
    $version = flutter --version 2>$null | Select-Object -First 1
    Write-Host " ✅ $version" -ForegroundColor Green
} else {
    Write-Host " ⚠️  Bulunamadı (opsiyonel)" -ForegroundColor Gray
}

# Backend dependencies
Write-Host "[6/8] Backend setup..." -NoNewline
if (Test-Path "backend\venv") {
    Write-Host " ✅ Virtual environment mevcut" -ForegroundColor Green
} else {
    Write-Host " ⚠️  Virtual environment yok" -ForegroundColor Yellow
    Write-Host "      Çalıştır: .\start-backend.ps1" -ForegroundColor Yellow
}

# .env dosyası
Write-Host "[7/8] Konfigürasyon..." -NoNewline
if (Test-Path "backend\.env") {
    Write-Host " ✅ .env dosyası mevcut" -ForegroundColor Green
} else {
    Write-Host " ❌ .env dosyası eksik!" -ForegroundColor Red
    Write-Host "      Oluştur: Copy backend\.env.example backend\.env" -ForegroundColor Yellow
    $allOk = $false
}

# Database seed
Write-Host "[8/8] Database seed..." -NoNewline
Set-Location "$PSScriptRoot\backend"
try {
    if (Test-Path "venv\Scripts\Activate.ps1") {
        & ".\venv\Scripts\Activate.ps1"
        $result = python -c "from sqlalchemy import create_engine, text; from app.core.config import settings; engine = create_engine(settings.DATABASE_URL); conn = engine.connect(); result = conn.execute(text('SELECT COUNT(*) FROM trap_types')); print(result.fetchone()[0])" 2>$null
        if ($result -eq "20") {
            Write-Host " ✅ Trap types seeded (20)" -ForegroundColor Green
        } else {
            Write-Host " ⚠️  Seed gerekli" -ForegroundColor Yellow
            Write-Host "      Çalıştır: .\setup-database.ps1" -ForegroundColor Yellow
        }
    } else {
        Write-Host " ⚠️  Backend kurulmamış" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Kontrol edilemedi" -ForegroundColor Yellow
}

Set-Location $PSScriptRoot

Write-Host "`n=====================================" -ForegroundColor Cyan
if ($allOk) {
    Write-Host "✅ SİSTEM HAZIR!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Sonraki adımlar:" -ForegroundColor Cyan
    Write-Host "1. .\start-backend.ps1      (Backend başlat)" -ForegroundColor White
    Write-Host "2. .\setup-database.ps1     (Database setup - ilk kez)" -ForegroundColor White
} else {
    Write-Host "❌ EKSİKLER VAR!" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Yukarıdaki eksiklikleri tamamlayın" -ForegroundColor Yellow
}
Write-Host ""
