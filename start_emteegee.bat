@echo off
title EMTeeGee Complete System Startup
color 0A

echo.
echo ================================================
echo        🚀 EMTeeGee Complete System Startup 🚀
echo ================================================
echo.
echo This script will start all required services:
echo   • MongoDB Database (Remote Atlas)
echo   • Ollama LLM Server  
echo   • Django Web Application
echo   • Cloudflare Tunnel
echo   • Desktop Worker
echo   • Swarm Dashboard
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Change to project directory
cd /d "C:\Users\Owner\Code\emteegee"

echo.
echo 🤖 Step 1/5: Starting Ollama LLM Server...
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

echo 🌐 Step 2/5: Starting Django Web Application...
echo ----------------------------------------
echo Starting Django app in new window...
start "EMTeeGee Django App - DO NOT CLOSE" cmd /c "title EMTeeGee Django App - DO NOT CLOSE && echo Django App Starting... && echo Web app will be available at http://localhost:8001 && echo Keep this window open! && python manage.py runserver 8001"
echo ✅ Django application window opened
echo ⏳ Waiting 5 seconds for Django to initialize...
timeout /t 5 /nobreak >nul

echo 🌩️  Step 3/5: Starting Cloudflare Tunnel...
echo ----------------------------------------
echo Starting Cloudflare tunnel with emteegee subdomain...
start "Cloudflare Tunnel - DO NOT CLOSE" cmd /c "title Cloudflare Tunnel - DO NOT CLOSE && echo Cloudflare Tunnel Starting... && echo Routes emteegee.tcgplex.com to local Django && echo This provides external access to your app && echo Keep this window open! && cloudflared tunnel --config tunnel-config.yml run"
echo ✅ Cloudflare tunnel window opened with new config
echo ⏳ Waiting 5 seconds for tunnel to connect both domains...
timeout /t 5 /nobreak >nul

echo 🐝 Step 4/5: Starting Desktop Worker...
echo ----------------------------------------
echo Starting Desktop Worker in new window...
start "EMTeeGee Desktop Worker - DO NOT CLOSE" cmd /c "title EMTeeGee Desktop Worker - DO NOT CLOSE && echo Desktop Worker Starting... && echo This handles AI analysis tasks && echo Keep this window open! && python desktop_worker_clean.py"
echo ✅ Desktop worker window opened
echo ⏳ Waiting 3 seconds for worker to initialize...
timeout /t 3 /nobreak >nul

echo 📊 Step 5/5: Starting Swarm Dashboard...
echo ----------------------------------------
echo Starting Swarm Dashboard in new window...
start "EMTeeGee Swarm Dashboard" cmd /c "title EMTeeGee Swarm Dashboard && echo Swarm Dashboard Interface && echo Use this to monitor system progress && echo Keep this window open for monitoring && python swarm_dashboard.py"
echo ✅ Swarm dashboard window opened
echo.

echo ================================================
echo           🎉 STARTUP COMPLETE! 🎉
echo ================================================
echo.
echo 📋 Services Started:
echo   ✅ Ollama LLM Server (http://localhost:11434)
echo   ✅ Django Web App (http://localhost:8001) 
echo   ✅ Cloudflare Tunnel (dual-domain config)
echo   ✅ Desktop Worker (AI Analysis)
echo   ✅ Swarm Dashboard (Monitoring)
echo.
echo 🌐 Access Points:
echo   • Local Django: http://localhost:8001
echo   • External: https://emteegee.tcgplex.com (subdomain)
echo   • API: https://emteegee.tcgplex.com/api/swarm/
echo.
echo 📊 Database:
echo   • MongoDB Atlas (Remote) - Check .env file
echo   • Cards Collection: 29,448+ cards
echo   • Distributed processing enabled
echo.
echo 💡 Next Steps:
echo   1. Check the Dashboard window for system status
echo   2. Monitor worker progress and task completion
echo   3. Test external access via https://emteegee.tcgplex.com
echo   4. Start laptop worker on second machine
echo   5. Scale up with additional workers as needed
echo.
echo 🔧 If any service fails:
echo   • Check the individual service windows for errors
echo   • Verify .env file configuration
echo   • Ensure MongoDB Atlas connection is working
echo   • Check Ollama model availability
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
