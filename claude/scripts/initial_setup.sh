#!/bin/bash
# EMTeeGee VPS Initial Setup Script
# Run with: curl -sSL https://raw.githubusercontent.com/yourusername/emteegee/main/claude/scripts/initial_setup.sh | bash

set -e

echo "🚀 Starting EMTeeGee VPS Setup..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Create application user
echo "👤 Creating emteegee user..."
if ! id "emteegee" &>/dev/null; then
    adduser --disabled-password --gecos "" emteegee
    usermod -aG sudo emteegee
fi

# Install required packages
echo "📋 Installing required packages..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    git \
    ufw \
    certbot \
    python3-certbot-nginx \
    curl \
    wget \
    htop \
    nano \
    unzip

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Create necessary directories
echo "📁 Creating directories..."
sudo -u emteegee mkdir -p /home/emteegee/logs
sudo -u emteegee mkdir -p /home/emteegee/backups

# Set timezone (adjust as needed)
echo "🕐 Setting timezone..."
timedatectl set-timezone UTC

# Configure automatic security updates
echo "🔒 Configuring automatic security updates..."
apt install -y unattended-upgrades
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades

# Optimize system for web serving
echo "⚡ Optimizing system..."
# Increase file limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Basic sysctl optimizations
cat >> /etc/sysctl.conf << EOF
# EMTeeGee optimizations
net.core.somaxconn = 1024
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 1024
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 120
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_keepalive_intvl = 30
EOF
sysctl -p

# Create deployment script
echo "📝 Creating deployment helper script..."
cat > /home/emteegee/deploy.sh << 'EOF'
#!/bin/bash
# EMTeeGee Deployment Helper Script

cd /home/emteegee/emteegee

echo "🔄 Pulling latest code..."
git pull

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing/updating dependencies..."
pip install -r requirements.txt

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔧 Checking Django configuration..."
python manage.py check

echo "♻️  Restarting services..."
sudo systemctl restart emteegee
sudo systemctl reload nginx

echo "✅ Deployment complete!"
EOF

chown emteegee:emteegee /home/emteegee/deploy.sh
chmod +x /home/emteegee/deploy.sh

# Create backup script
echo "💾 Creating backup script..."
cat > /home/emteegee/backup.sh << 'EOF'
#!/bin/bash
# EMTeeGee Backup Script

BACKUP_DIR="/home/emteegee/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Creating backup: $DATE"

# Backup application code
tar -czf "$BACKUP_DIR/emteegee_code_$DATE.tar.gz" -C /home/emteegee emteegee

# Backup nginx config
sudo cp /etc/nginx/sites-available/emteegee "$BACKUP_DIR/nginx_config_$DATE"

# Backup systemd service
sudo cp /etc/systemd/system/emteegee.service "$BACKUP_DIR/systemd_service_$DATE"

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "nginx_config_*" -mtime +7 -delete
find "$BACKUP_DIR" -name "systemd_service_*" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_DIR"
EOF

chown emteegee:emteegee /home/emteegee/backup.sh
chmod +x /home/emteegee/backup.sh

# Setup daily backup cron job
echo "⏰ Setting up daily backups..."
(crontab -u emteegee -l 2>/dev/null; echo "0 2 * * * /home/emteegee/backup.sh") | crontab -u emteegee -

# Configure log rotation
echo "📝 Configuring log rotation..."
cat > /etc/logrotate.d/emteegee << EOF
/home/emteegee/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 emteegee emteegee
    postrotate
        systemctl reload emteegee
    endscript
}
EOF

echo "✅ Initial setup complete!"
echo ""
echo "Next steps:"
echo "1. Switch to emteegee user: su - emteegee"
echo "2. Clone your repository: git clone https://github.com/yourusername/emteegee.git"
echo "3. Run the Django setup script: ~/emteegee/claude/scripts/django_setup.sh"
echo "4. Configure Nginx and SSL"
echo ""
echo "🎉 Your VPS is ready for EMTeeGee deployment!"
