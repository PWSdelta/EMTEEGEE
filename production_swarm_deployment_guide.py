#!/usr/bin/env python3
"""
Production Server Swarm API Deployment Guide
Steps to deploy the swarm system to your production server
"""

print("""
🚀 EMTEEGEE Swarm API Production Deployment Guide
================================================

PROBLEM: Your production server (64.23.130.187:8000) is missing the swarm API routes.
The 404 errors in your logs confirm this:
  - "POST /api/swarm/register HTTP/1.1" 404 6345
  - "GET /api/swarm/status HTTP/1.1" 404 6338

SOLUTION: Deploy the swarm system to production server.

📋 Files that need to be deployed to production:
==============================================

1. 📁 cards/swarm_api.py               ✅ (Swarm API endpoints)
2. 📁 cards/api_urls.py                ✅ (API URL routing) 
3. 📁 swarm_manager_simple.py          ✅ (Swarm manager)
4. 📁 emteegee/urls.py                 ✅ (Main URL config - must include swarm routes)

🔧 Key Configuration Check:
==========================

Your production emteegee/urls.py MUST include this line:
    path('api/swarm/', include('cards.api_urls')),

📤 Deployment Steps:
==================

OPTION A: Full Repository Sync
------------------------------
1. Commit your latest changes locally:
   git add .
   git commit -m "Add swarm API system"
   git push origin main

2. On production server:
   git pull origin main
   python manage.py collectstatic --noinput
   sudo systemctl restart your-django-service

OPTION B: Manual File Upload
----------------------------
Upload these specific files to production:
- cards/swarm_api.py
- cards/api_urls.py  
- swarm_manager_simple.py
- emteegee/urls.py (with swarm routes)

OPTION C: Test Locally First
-----------------------------
1. Test swarm API locally:
   python manage.py runserver 8001
   python test_worker_connection.py

2. Verify these URLs work:
   http://localhost:8001/api/swarm/status
   http://localhost:8001/api/swarm/register

3. Deploy to production once local testing passes

🧪 Verification Commands:
========================

After deployment, test these URLs on production:
- https://your-domain.com/api/swarm/status
- http://64.23.130.187:8000/api/swarm/status

Expected response:
{
  "workers": {"total": 0, "active": 0, "offline": 0},
  "tasks": {"pending": 0, "completed": 0},
  "analysis": {"total_cards": 29448, "analyzed_cards": X, "progress_percentage": Y}
}

🐛 Common Issues:
================

1. URL routing not included in main urls.py
2. Missing cards/api_urls.py file
3. SwarmManager import errors
4. MongoDB connection issues on production

💡 Quick Test:
=============

Run this on your production server to check if swarm routes exist:
    python manage.py show_urls | grep swarm

If no results, the swarm routes aren't configured.

🎯 Next Steps:
=============

1. ✅ Verify local swarm API works (we confirmed this)
2. 🔄 Deploy swarm files to production
3. ✅ Test production swarm API endpoints
4. 🚀 Run distributed workers

Once the swarm API is deployed to production, your workers will be able to:
- Register with the remote server
- Receive work assignments
- Submit analysis results
- Participate in distributed AI analysis

""")

if __name__ == "__main__":
    pass
