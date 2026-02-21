# YÖKDİL Health App - Database Setup Script
# İlk kurulum için

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "YÖKDİL HEALTH APP - Database Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "$PSScriptRoot\backend"

# Virtual environment aktif et
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[1/4] Virtual environment aktif ediliyor..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment aktif" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment bulunamadı!" -ForegroundColor Red
    Write-Host "Önce 'start-backend.ps1' scriptini çalıştırın" -ForegroundColor Red
    exit 1
}

# Alembic migration
Write-Host "`n[2/4] Database migration çalıştırılıyor..." -ForegroundColor Yellow
try {
    alembic upgrade head
    Write-Host "✅ Migration tamamlandı" -ForegroundColor Green
} catch {
    Write-Host "❌ Migration hatası: $_" -ForegroundColor Red
    exit 1
}

# Trap types seed (ZORUNLU!)
Write-Host "`n[3/4] Trap types seed ediliyor (20 trap type)..." -ForegroundColor Yellow
try {
    python scripts\seed_trap_types.py
    Write-Host "✅ Trap types seed edildi" -ForegroundColor Green
} catch {
    Write-Host "❌ Seed hatası: $_" -ForegroundColor Red
    Write-Host "Manuel olarak çalıştırın: python scripts\seed_trap_types.py" -ForegroundColor Yellow
}

# Demo data (OPSIYONEL)
Write-Host "`n[4/4] Demo data seed edilsin mi? (y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "y" -or $response -eq "Y") {
    try {
        python scripts\seed_demo_data.py
        Write-Host "✅ Demo data seed edildi" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Demo data seed hatası (opsiyonel, devam edebilirsiniz)" -ForegroundColor Yellow
    }
} else {
    Write-Host "Demo data atlandı" -ForegroundColor Gray
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "✅ DATABASE SETUP TAMAMLANDI!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Sonraki adım: Backend başlatın" -ForegroundColor Cyan
Write-Host "Komut: .\start-backend.ps1" -ForegroundColor White
Write-Host ""
