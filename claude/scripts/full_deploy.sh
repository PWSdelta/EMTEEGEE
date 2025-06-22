#!/bin/bash
# Full EMTeeGee Deployment Script
# Run as root on fresh server

set -e

echo "🚀 Starting full EMTeeGee deployment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Get GitHub username and domain
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your domain (e.g., mtgabyss.com): " DOMAIN

if [ -z "$GITHUB_USER" ] || [ -z "$DOMAIN" ]; then
    echo "❌ GitHub username and domain are required"
    exit 1
fi

echo "📋 Deploying ${GITHUB_USER}/emteegee to ${DOMAIN}"

# Step 1: Switch to emteegee user and clone repository
echo "📦 Cloning repository..."
sudo -u emteegee bash << EOF
cd /home/emteegee
if [ -d "emteegee" ]; then
    echo "Repository already exists, pulling latest..."
    cd emteegee
    git pull
else
    git clone https://github.com/${GITHUB_USER}/emteegee.git
    cd emteegee
fi

# Make scripts executable
chmod +x claude/scripts/*.sh

# Run Django setup
./claude/scripts/django_setup.sh

# Activate venv and install production dependencies
source venv/bin/activate
pip install -r claude/requirements_production.txt
pip install -r requirements.txt

echo "✅ Application setup complete"
EOF

# Step 2: Configure services
echo "⚙️ Configuring services..."
/home/emteegee/emteegee/claude/scripts/configure_services.sh << EOF
${DOMAIN}
EOF

# Step 3: Test configuration
echo "🧪 Testing configuration..."
nginx -t
systemctl is-active emteegee && echo "✅ EMTeeGee service running" || echo "❌ EMTeeGee service failed"
systemctl is-active nginx && echo "✅ Nginx running" || echo "❌ Nginx failed"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your app should be available at: http://${DOMAIN}"
echo ""
echo "📋 Next steps:"
echo "1. Point your domain DNS to this server IP"
echo "2. Wait 5-15 minutes for DNS propagation"
echo "3. Setup SSL: sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo "4. Test API endpoints"
echo "5. Update workers to use https://${DOMAIN}"
echo ""
echo "🎉 Welcome to production!"
