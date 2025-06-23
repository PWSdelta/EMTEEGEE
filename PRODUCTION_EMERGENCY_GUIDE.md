"""
EMTEEGEE PRODUCTION DEPLOYMENT EMERGENCY GUIDE
===============================================

PROBLEM DIAGNOSIS: Django is not running on the production server
- All endpoints return 502 Bad Gateway
- Nginx is running but can't connect to Django
- Enhanced Swarm API v3.0 is ready but Django needs to be started

IMMEDIATE ACTION REQUIRED:
========================

Step 1: SSH to Production Server
--------------------------------
ssh your_username@your_production_server

Step 2: Navigate to Django Directory  
------------------------------------
cd /var/www/emteegee
# (or wherever your Django project is deployed)

Step 3: Quick Status Check
-------------------------
# Check if Django is running
ps aux | grep -E "python.*manage.py|gunicorn.*emteegee"

# Check if the port is in use
netstat -tlnp | grep :8000

Step 4: Start Django
--------------------
# Option A: Using the deployment script (RECOMMENDED)
bash deploy_production.sh

# Option B: Manual start with Gunicorn (if available)
gunicorn emteegee.wsgi:application --bind 0.0.0.0:8000 --workers 3 --daemon

# Option C: Manual start with manage.py
nohup python manage.py runserver 0.0.0.0:8000 &

Step 5: Verify Django is Running
--------------------------------
# Check processes
ps aux | grep -E "python.*manage.py|gunicorn.*emteegee"

# Test locally on server
curl http://localhost:8000/api/enhanced_swarm/status

# Check from your local machine
python simple_status_check.py

Step 6: Restart Nginx (if needed)
---------------------------------
sudo systemctl restart nginx

DEPLOYMENT SCRIPT CONTENTS:
===========================
The deploy_production.sh script will:
✅ Pull latest code from GitHub
✅ Install/update Python dependencies  
✅ Run Django system checks
✅ Apply database migrations
✅ Collect static files
✅ Stop any existing Django processes
✅ Start Django with Gunicorn or manage.py
✅ Test endpoints
✅ Restart Nginx

TROUBLESHOOTING:
===============

If Django won't start:
1. Check Python virtual environment is activated
2. Check if all dependencies are installed: pip install -r requirements.txt
3. Check Django settings: python manage.py check
4. Check database connection: python manage.py migrate
5. Check for port conflicts: netstat -tlnp | grep :8000

If Enhanced API returns errors:
1. Check that cards/enhanced_swarm_api.py exists
2. Check that cards/enhanced_api_urls.py exists  
3. Check that emteegee/urls.py includes enhanced API routes
4. Check Django logs for import errors

Common Issues:
- Port 8000 already in use: kill existing process or use different port
- Permission errors: check file permissions and ownership
- Import errors: missing dependencies or Python path issues
- Database errors: run migrations or check database connection

VERIFICATION COMMANDS:
====================

From your local machine:
------------------------
# Check status
python simple_status_check.py

# Test enhanced API specifically
curl https://mtgabyss.com/api/enhanced_swarm/status

# Start workers once Django is running
python universal_worker_enhanced.py --server https://mtgabyss.com

From production server:
----------------------
# Check Django process
ps aux | grep -E "python.*manage.py|gunicorn.*emteegee"

# Check port
netstat -tlnp | grep :8000

# Test locally
curl http://localhost:8000/api/enhanced_swarm/status

# Check logs
tail -f nohup.out
# or
journalctl -u your_django_service -f

EXPECTED RESULTS:
================

When working correctly:
✅ https://mtgabyss.com/ - Returns Django site (not 502)
✅ https://mtgabyss.com/admin/ - Returns Django admin login
✅ https://mtgabyss.com/api/enhanced_swarm/status - Returns JSON with API status
✅ https://mtgabyss.com/api/enhanced_swarm/workers - Returns JSON with worker list

SUCCESS INDICATORS:
==================
- simple_status_check.py shows "DJANGO IS RUNNING - READY FOR WORKERS!"
- All 4 endpoints return 200 OK instead of 502 Bad Gateway
- Enhanced API returns proper JSON responses
- Workers can register and get work assignments

NEXT STEPS AFTER DJANGO IS RUNNING:
==================================
1. Verify all endpoints work: python simple_status_check.py
2. Start distributed workers: python universal_worker_enhanced.py --server https://mtgabyss.com
3. Monitor worker activity via enhanced API endpoints
4. Scale up with multiple worker instances across different machines

CONTACT INFORMATION:
===================
If you need help, the enhanced swarm system includes:
- Enhanced logging in cards/swarm_logging.py
- System metrics at /api/enhanced_swarm/metrics
- Worker health monitoring at /api/enhanced_swarm/workers
- Comprehensive error handling and status reporting
"""
