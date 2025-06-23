#!/bin/bash

# EMTEEGEE Production Deployment & Django Restart Script
# This script helps deploy the enhanced swarm API and restart Django on production

echo "=== EMTEEGEE PRODUCTION DEPLOYMENT SCRIPT ==="
echo "Enhanced Swarm API v3.0 Production Setup"
echo ""

# Check if we're on the production server
if [ ! -d "/var/www/emteegee" ]; then
    echo "❌ Error: This script should be run on the production server where Django is installed"
    echo "Expected path: /var/www/emteegee"
    exit 1
fi

echo "✅ Found production directory: /var/www/emteegee"

# Step 1: Pull latest code
echo ""
echo "📥 Step 1: Pulling latest code from GitHub..."
cd /var/www/emteegee
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull latest code"
    exit 1
fi
echo "✅ Latest code pulled successfully"

# Step 2: Check Django configuration
echo ""
echo "🔧 Step 2: Checking Django configuration..."

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found in /var/www/emteegee"
    exit 1
fi
echo "✅ Django manage.py found"

# Check if enhanced API files exist
if [ ! -f "cards/enhanced_swarm_api.py" ]; then
    echo "❌ Error: Enhanced API file not found: cards/enhanced_swarm_api.py"
    exit 1
fi

if [ ! -f "cards/enhanced_api_urls.py" ]; then
    echo "❌ Error: Enhanced API URLs not found: cards/enhanced_api_urls.py"
    exit 1
fi
echo "✅ Enhanced API files found"

# Step 3: Install/update dependencies
echo ""
echo "📦 Step 3: Installing/updating Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to install some dependencies, continuing..."
fi

# Step 4: Run Django checks
echo ""
echo "🔍 Step 4: Running Django system checks..."
python manage.py check

if [ $? -ne 0 ]; then
    echo "❌ Error: Django configuration has errors"
    echo "Please fix Django errors before proceeding"
    exit 1
fi
echo "✅ Django configuration is valid"

# Step 5: Apply database migrations
echo ""
echo "🗄️  Step 5: Applying database migrations..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Migration issues detected, continuing..."
fi

# Step 6: Collect static files
echo ""
echo "📁 Step 6: Collecting static files..."
python manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Static file collection issues, continuing..."
fi

# Step 7: Find and stop any running Django processes
echo ""
echo "🛑 Step 7: Stopping existing Django processes..."

# Find Django processes
DJANGO_PIDS=$(pgrep -f "python.*manage.py.*runserver\|gunicorn.*emteegee")

if [ ! -z "$DJANGO_PIDS" ]; then
    echo "Found running Django/Gunicorn processes: $DJANGO_PIDS"
    echo "Stopping processes..."
    kill $DJANGO_PIDS
    sleep 3
    
    # Force kill if still running
    DJANGO_PIDS=$(pgrep -f "python.*manage.py.*runserver\|gunicorn.*emteegee")
    if [ ! -z "$DJANGO_PIDS" ]; then
        echo "Force killing remaining processes..."
        kill -9 $DJANGO_PIDS
    fi
    echo "✅ Stopped existing Django processes"
else
    echo "✅ No existing Django processes found"
fi

# Step 8: Start Django
echo ""
echo "🚀 Step 8: Starting Django application..."

# Try to start with Gunicorn (production recommended)
if command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn (production mode)..."
    nohup gunicorn emteegee.wsgi:application --bind 0.0.0.0:8000 --workers 3 --daemon
    
    if [ $? -eq 0 ]; then
        echo "✅ Django started with Gunicorn on port 8000"
    else
        echo "⚠️  Gunicorn failed, trying with manage.py runserver..."
        nohup python manage.py runserver 0.0.0.0:8000 &
        echo "✅ Django started with runserver on port 8000"
    fi
else
    echo "Gunicorn not found, starting with manage.py runserver..."
    nohup python manage.py runserver 0.0.0.0:8000 &
    echo "✅ Django started with runserver on port 8000"
fi

# Step 9: Wait and test
echo ""
echo "⏳ Step 9: Waiting for Django to start..."
sleep 5

# Test if Django is responding
echo "Testing Django endpoints..."

# Test basic Django
curl -s -f http://localhost:8000/admin/ > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Django admin is responding"
else
    echo "❌ Django admin is not responding"
fi

# Test enhanced API
curl -s -f http://localhost:8000/api/enhanced_swarm/status > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Enhanced Swarm API is responding"
else
    echo "❌ Enhanced Swarm API is not responding"
fi

# Step 10: Restart Nginx
echo ""
echo "🔄 Step 10: Restarting Nginx..."
sudo systemctl restart nginx

if [ $? -eq 0 ]; then
    echo "✅ Nginx restarted successfully"
else
    echo "❌ Failed to restart Nginx"
fi

# Final status
echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "🌐 Test URLs:"
echo "   • Main site: https://mtgabyss.com/"
echo "   • Admin: https://mtgabyss.com/admin/"
echo "   • Enhanced API Status: https://mtgabyss.com/api/enhanced_swarm/status"
echo "   • Enhanced API Workers: https://mtgabyss.com/api/enhanced_swarm/workers"
echo ""
echo "📋 Next Steps:"
echo "   1. Test the URLs above in your browser"
echo "   2. If working, start universal workers with:"
echo "      python universal_worker_enhanced.py --server https://mtgabyss.com"
echo "   3. Monitor logs: tail -f nohup.out"
echo ""

# Show running processes
echo "🔍 Current Django processes:"
ps aux | grep -E "python.*manage.py|gunicorn.*emteegee" | grep -v grep
