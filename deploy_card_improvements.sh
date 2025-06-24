#!/bin/bash
# Deployment script for card detail page improvements

echo "🚀 Deploying Card Detail Page Improvements"
echo "=========================================="

echo "📥 Pulling latest changes from repository..."
git pull origin main

echo "🔄 Checking for any new requirements..."
pip install -r requirements.txt

echo "📋 Running database migrations (if any)..."
python manage.py migrate

echo "🗂️  Collecting static files..."
python manage.py collectstatic --noinput

echo "♻️  Restarting services..."
# Uncomment the appropriate restart commands for your server setup:

# For systemd services:
# sudo systemctl restart emteegee
# sudo systemctl restart nginx

# For PM2:
# pm2 restart emteegee

# For direct gunicorn:
# pkill -f gunicorn
# nohup gunicorn emteegee.wsgi:application --bind 0.0.0.0:8000 &

echo "✅ Deployment Complete!"
echo ""
echo "🧪 Test the improvements at:"
echo "   - Card Detail Page: https://yourdomain.com/card/[uuid]/"
echo "   - Browse Cards: https://yourdomain.com/browse/"
echo ""
echo "🎯 Key Improvements Deployed:"
echo "   ✅ Full component analysis display (no truncation)"
echo "   ✅ Proper markdown rendering"
echo "   ✅ Individual component expand/collapse"
echo "   ✅ Enhanced typography and styling"
echo "   ✅ Better readability for analysis evaluation"
echo ""
echo "📊 You can now properly evaluate AI analysis quality!"
