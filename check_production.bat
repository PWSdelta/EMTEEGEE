@echo off
echo =================================
echo EMTEEGEE PRODUCTION STATUS CHECK
echo =================================
echo.

cd /d "c:\Users\Owner\Code\emteegee"
python simple_status_check.py

echo.
echo =================================
echo QUICK ACTIONS:
echo =================================
echo.
echo If Django is NOT running:
echo 1. SSH to your production server
echo 2. cd /var/www/emteegee
echo 3. bash deploy_production.sh
echo.
echo If Django IS running:
echo 1. Start workers: python universal_worker_enhanced.py --server https://mtgabyss.com
echo 2. Monitor: python swarm_dashboard.py
echo.
pause
