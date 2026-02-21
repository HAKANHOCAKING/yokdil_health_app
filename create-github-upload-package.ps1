# 📦 GitHub Web Upload Paketi Oluştur
# Git kurulu değilse bu yöntemi kullan

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "📦 GITHUB WEB UPLOAD PAKETI" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "C:\Users\90505\yokdil_health_app"
$outputPath = "$env:USERPROFILE\Desktop\yokdil-health-app-upload.zip"

Write-Host "[1/3] Dosyalar hazırlanıyor..." -ForegroundColor Yellow

# Geçici dizin
$tempDir = "$env:TEMP\yokdil-upload-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Hariç tutulacak dosyalar/klasörler
$excludePatterns = @(
    "node_modules",
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    "venv",
    "env",
    ".env",
    "*.db",
    "*.sqlite",
    ".DS_Store",
    "Thumbs.db",
    "*.log",
    ".git",
    "build",
    "dist"
)

Write-Host "Dosyalar kopyalanıyor..." -ForegroundColor Gray

# Tüm dosyaları kopyala (hariç tutulanlar dışında)
Get-ChildItem -Path $projectPath -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Replace($projectPath, "")
    $shouldExclude = $false
    
    foreach ($pattern in $excludePatterns) {
        if ($relativePath -like "*$pattern*") {
            $shouldExclude = $true
            break
        }
    }
    
    if (-not $shouldExclude) {
        $destPath = Join-Path $tempDir $relativePath
        $destDir = Split-Path $destPath
        
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        if (-not $_.PSIsContainer) {
            Copy-Item $_.FullName -Destination $destPath -Force
        }
    }
}

Write-Host "✅ Dosyalar hazır" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] ZIP oluşturuluyor..." -ForegroundColor Yellow

# ZIP oluştur
if (Test-Path $outputPath) {
    Remove-Item $outputPath -Force
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $outputPath -CompressionLevel Optimal

# Temizlik
Remove-Item $tempDir -Recurse -Force

Write-Host "✅ ZIP oluşturuldu" -ForegroundColor Green

Write-Host ""
Write-Host "[3/3] Hazır!" -ForegroundColor Yellow
Write-Host ""

# Dosya boyutu
$zipSize = (Get-Item $outputPath).Length / 1MB
Write-Host "📦 Dosya: $outputPath" -ForegroundColor Cyan
Write-Host "📊 Boyut: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "✅ PAKET HAZIR!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "ŞİMDİ NE YAPMALISIN:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. GitHub'a Git:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Repository Oluştur:" -ForegroundColor White
Write-Host "   Name: yokdil-health-app" -ForegroundColor Gray
Write-Host "   'Create repository' tıkla" -ForegroundColor Gray
Write-Host ""
Write-Host "3. ZIP Yükle:" -ForegroundColor White
Write-Host "   'uploading an existing file' linkine tıkla" -ForegroundColor Gray
Write-Host "   Desktop'taki ZIP'i sürükle" -ForegroundColor Gray
Write-Host "   'Commit changes' tıkla" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Railway'e Geç:" -ForegroundColor White
Write-Host "   https://railway.app/" -ForegroundColor Cyan
Write-Host "   RAILWAY_ADIM_ADIM.md dosyasını takip et" -ForegroundColor Gray
Write-Host ""

# Masaustu ac
Write-Host "Masaustu aciliyor..." -ForegroundColor Gray
Start-Process "explorer.exe" -ArgumentList "/select,""$outputPath"""

Write-Host ""
Write-Host "HAZIR! ZIP dosyasi masaustunde" -ForegroundColor Green
Write-Host ""
