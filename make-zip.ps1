# Simple GitHub Upload Package Creator

$projectPath = "C:\Users\90505\yokdil_health_app"
$outputZip = "C:\Users\90505\yokdil-health-app-github.zip"

Write-Host "Creating GitHub upload package..." -ForegroundColor Cyan
Write-Host ""

# Create ZIP directly
if (Test-Path $outputZip) {
    Remove-Item $outputZip -Force
}

# Exclude folders
$excludeFolders = @("venv", "__pycache__", "node_modules", ".git", "build", "dist")

Write-Host "Compressing project..." -ForegroundColor Yellow

# Get all files except excluded
$filesToZip = Get-ChildItem -Path $projectPath -Recurse -File | Where-Object {
    $file = $_
    $shouldInclude = $true
    
    foreach ($exclude in $excludeFolders) {
        if ($file.FullName -like "*\$exclude\*") {
            $shouldInclude = $false
            break
        }
    }
    
    # Exclude specific files
    if ($file.Name -eq ".env" -or $file.Extension -eq ".pyc" -or $file.Extension -eq ".log") {
        $shouldInclude = $false
    }
    
    $shouldInclude
}

# Create ZIP
$tempDir = "$env:TEMP\yokdil-temp"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

foreach ($file in $filesToZip) {
    $relativePath = $file.FullName.Replace($projectPath, "")
    $destPath = Join-Path $tempDir $relativePath
    $destDir = Split-Path $destPath
    
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    Copy-Item $file.FullName -Destination $destPath -Force
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $outputZip -CompressionLevel Optimal
Remove-Item $tempDir -Recurse -Force

$sizeMB = [math]::Round((Get-Item $outputZip).Length / 1MB, 2)

Write-Host ""
Write-Host "SUCCESS!" -ForegroundColor Green
Write-Host ""
Write-Host "ZIP File: $outputZip" -ForegroundColor Cyan
Write-Host "Size: $sizeMB MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "2. Name: yokdil-health-app" -ForegroundColor White
Write-Host "3. Create repository" -ForegroundColor White
Write-Host "4. Upload ZIP file" -ForegroundColor White
Write-Host "5. Go to Railway: https://railway.app/" -ForegroundColor White
Write-Host ""

# Open folder
Start-Process "explorer.exe" -ArgumentList "/select,""$outputZip"""

Write-Host "ZIP location opened in Explorer!" -ForegroundColor Green
