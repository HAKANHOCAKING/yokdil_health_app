# GitHub Web Upload Package Creator
# Use this if Git is not installed

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "GitHub Web Upload Package Creator" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = "C:\Users\90505\yokdil_health_app"
$outputPath = "$env:USERPROFILE\Desktop\yokdil-health-app-upload.zip"

Write-Host "[1/3] Preparing files..." -ForegroundColor Yellow

# Temp directory
$tempDir = "$env:TEMP\yokdil-upload-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Exclude patterns
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

Write-Host "Copying files..." -ForegroundColor Gray

# Copy all files (except excluded)
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

Write-Host "Done: Files ready" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] Creating ZIP..." -ForegroundColor Yellow

# Create ZIP
if (Test-Path $outputPath) {
    Remove-Item $outputPath -Force
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $outputPath -CompressionLevel Optimal

# Cleanup
Remove-Item $tempDir -Recurse -Force

Write-Host "Done: ZIP created" -ForegroundColor Green

Write-Host ""
Write-Host "[3/3] Ready!" -ForegroundColor Yellow
Write-Host ""

# File size
$zipSize = (Get-Item $outputPath).Length / 1MB
Write-Host "File: $outputPath" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "PACKAGE READY!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "WHAT TO DO NOW:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Go to GitHub:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Create Repository:" -ForegroundColor White
Write-Host "   Name: yokdil-health-app" -ForegroundColor Gray
Write-Host "   Click 'Create repository'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Upload ZIP:" -ForegroundColor White
Write-Host "   Click 'uploading an existing file'" -ForegroundColor Gray
Write-Host "   Drag the ZIP from Desktop" -ForegroundColor Gray
Write-Host "   Click 'Commit changes'" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Go to Railway:" -ForegroundColor White
Write-Host "   https://railway.app/" -ForegroundColor Cyan
Write-Host "   Follow RAILWAY_ADIM_ADIM.md" -ForegroundColor Gray
Write-Host ""

# Open Desktop
Write-Host "Opening Desktop..." -ForegroundColor Gray
Start-Process "explorer.exe" -ArgumentList "/select,""$outputPath"""

Write-Host ""
Write-Host "READY! ZIP file is on Desktop" -ForegroundColor Green
Write-Host ""
