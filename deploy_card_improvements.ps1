# PowerShell Deployment Script for Windows Server
# deploy_card_improvements.ps1

Write-Host "🚀 Deploying Card Detail Page Improvements" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

Write-Host "📥 Pulling latest changes from repository..." -ForegroundColor Cyan
git pull origin main

Write-Host "🔄 Checking for any new requirements..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "📋 Running database migrations (if any)..." -ForegroundColor Cyan
python manage.py migrate

Write-Host "🗂️  Collecting static files..." -ForegroundColor Cyan
python manage.py collectstatic --noinput

Write-Host "♻️  Restarting services..." -ForegroundColor Cyan
# Uncomment the appropriate restart commands for your server setup:

# For Windows Service:
# Restart-Service -Name "EMTEEGEE"

# For IIS:
# iisreset

# For direct process (kill and restart):
# Get-Process -Name "python" | Where-Object {$_.CommandLine -like "*manage.py*"} | Stop-Process
# Start-Process python -ArgumentList "manage.py runserver 0.0.0.0:8000" -WindowStyle Hidden

Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🧪 Test the improvements at:" -ForegroundColor Yellow
Write-Host "   - Card Detail Page: https://yourdomain.com/card/[uuid]/" -ForegroundColor White
Write-Host "   - Browse Cards: https://yourdomain.com/browse/" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Key Improvements Deployed:" -ForegroundColor Yellow
Write-Host "   ✅ Full component analysis display (no truncation)" -ForegroundColor Green
Write-Host "   ✅ Proper markdown rendering" -ForegroundColor Green
Write-Host "   ✅ Individual component expand/collapse" -ForegroundColor Green
Write-Host "   ✅ Enhanced typography and styling" -ForegroundColor Green
Write-Host "   ✅ Better readability for analysis evaluation" -ForegroundColor Green
Write-Host ""
Write-Host "📊 You can now properly evaluate AI analysis quality!" -ForegroundColor Magenta
