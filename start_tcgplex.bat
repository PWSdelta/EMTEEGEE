@echo off
title TCGplex Complete System Startup
color 0A

echo.
echo ================================================
echo        🚀 TCGplex Complete System Startup 🚀
echo ================================================
echo.
echo This script will start all required services:
echo   • MongoDB Database
echo   • Ollama LLM Server  
echo   • Flask Web Application
echo   • Cloudflare Tunnel
echo   • Review Manager Interface
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Change to project directory
cd /d "C:\Users\Owner\Code\MagicAI"

echo.
echo 📊 Step 1/5: Starting MongoDB...
echo ----------------------------------------
net start MongoDB 2>nul
if %errorlevel% == 0 (
    echo ✅ MongoDB started successfully
) else (
    echo ℹ️  MongoDB already running or failed to start
    echo    (This is usually fine if it's already running)
)
echo.

echo 🤖 Step 2/5: Starting Ollama LLM Server...
echo ----------------------------------------
echo Starting Ollama in new window...
start "Ollama Server - DO NOT CLOSE" cmd /c "title Ollama Server - DO NOT CLOSE && echo Ollama Server Starting... && echo Keep this window open! && ollama serve"
echo ✅ Ollama server window opened
echo ⏳ Waiting 8 seconds for Ollama to initialize...
timeout /t 8 /nobreak >nul

REM Test Ollama connection with better error handling
echo 🧪 Testing Ollama connection...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; try { $response = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get -TimeoutSec 10; Write-Host '✅ Ollama is responding and ready!' -ForegroundColor Green } catch { Write-Host '⚠️  Ollama not responding yet (may need more time)' -ForegroundColor Yellow }"
echo.

echo 🌐 Step 3/5: Starting Flask Web Application...
echo ----------------------------------------
echo Starting Flask app in new window...
start "TCGplex Flask App - DO NOT CLOSE" cmd /c "title TCGplex Flask App - DO NOT CLOSE && echo Flask App Starting... && echo Web app will be available at http://localhost:5000 && echo Keep this window open! && C:/Users/Owner/Code/MagicAI/.venv/Scripts/python.exe app.py"
echo ✅ Flask application window opened
echo ⏳ Waiting 5 seconds for Flask to initialize...
timeout /t 5 /nobreak >nul

echo 🌩️  Step 4/5: Starting Cloudflare Tunnel...
echo ----------------------------------------
echo Starting Cloudflare tunnel with dual-domain config...
start "Cloudflare Tunnel - DO NOT CLOSE" cmd /c "title Cloudflare Tunnel - DO NOT CLOSE && echo Cloudflare Tunnel Starting... && echo Handles both tcgplex.com and www.tcgplex.com && echo This provides external access to your app && echo Keep this window open! && cloudflared tunnel --config tunnel-config.yml run"
echo ✅ Cloudflare tunnel window opened with new config
echo ⏳ Waiting 5 seconds for tunnel to connect both domains...
timeout /t 5 /nobreak >nul

echo ⚙️  Step 5/5: Starting Review Management Interface...
echo ----------------------------------------
echo Starting Review Manager in new window...
start "TCGplex Review Manager" cmd /c "title TCGplex Review Manager && echo Review Manager Interface && echo Use this to manage review generation && echo Tip: Choose option 9 for fresh start with 3 workers && C:/Users/Owner/Code/MagicAI/.venv/Scripts/python.exe tcgplex_mongo_manager.py"
echo ✅ Review manager window opened
echo.

echo ================================================
echo           🎉 STARTUP COMPLETE! 🎉
echo ================================================
echo.
echo 📋 Services Started:
echo   ✅ MongoDB Database (background service)
echo   ✅ Ollama LLM Server (http://localhost:11434)
echo   ✅ Flask Web App (http://localhost:5000) 
echo   ✅ Cloudflare Tunnel (dual-domain config)
echo   ✅ Review Manager Interface
echo.
echo 🌐 Access Points:
echo   • Local: http://localhost:5000
echo   • External: https://tcgplex.com (primary domain)
echo   • External: https://www.tcgplex.com (redirects to main)
echo   • ads.txt: https://tcgplex.com/ads.txt
echo.
echo 💡 Next Steps:
echo   1. In the Review Manager window, choose option 9
echo      (Fresh start - Clear + Queue + 3 Workers)
echo   2. Wait for initial reviews to generate
echo   3. Use option 11 for "Most Mentions" priority system
echo   4. Test ads.txt: https://tcgplex.com/ads.txt
echo   5. Verify no redirect loops on primary domain
echo.
echo 🔧 If any service fails:
echo   • Check the individual service windows for errors
echo   • Refer to STARTUP_GUIDE.md for troubleshooting
echo   • Ensure all dependencies are installed
echo.
echo ⚠️  IMPORTANT: Do not close the service windows!
echo    They need to stay open for the system to work.
echo.
echo Press any key to exit this script...
echo (The services will continue running in their own windows)
pause >nul

echo.
echo 👋 Startup script complete. Services are now running!
echo    Check the service windows for status updates.
echo.
