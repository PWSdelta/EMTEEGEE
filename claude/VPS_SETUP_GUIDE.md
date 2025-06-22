# EMTeeGee VPS Setup Guide
## Complete Linode Nanode Deployment

### 📋 Pre-Deployment Checklist

**Before You Start:**
- [ ] Linode account created
- [ ] Domain name purchased (optional but recommended)
- [ ] MongoDB Atlas connection string ready
- [ ] Local code tested and committed to Git

### 🚀 Step 1: Create Linode Server

**Server Specs:**
- **Plan**: Nanode 1GB ($5/month)
- **Region**: Choose closest to you (US East, Europe, etc.)
- **Image**: Ubuntu 22.04 LTS
- **Root Password**: Strong password
- **SSH Keys**: Add your public key

**Initial Access:**
```bash
ssh root@YOUR_SERVER_IP
```

### 🔧 Step 2: Server Initial Setup

Run our automated setup script:

```bash
# Download and run setup script
curl -sSL https://raw.githubusercontent.com/yourusername/emteegee/main/claude/scripts/initial_setup.sh | bash
```

**Or manual setup:**
```bash
# Update system
apt update && apt upgrade -y

# Create application user
adduser emteegee
usermod -aG sudo emteegee

# Install required packages
apt install -y python3 python3-pip python3-venv nginx git ufw certbot python3-certbot-nginx

# Configure firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
```

### 🐍 Step 3: Deploy Django Application

**Switch to app user:**
```bash
su - emteegee
```

**Clone and setup application:**
```bash
# Clone your repository
git clone https://github.com/yourusername/emteegee.git
cd emteegee

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
nano .env  # Edit with your MongoDB Atlas connection, etc.

# Test Django
python manage.py collectstatic --noinput
python manage.py check
```

### 🌐 Step 4: Configure Nginx

**Create Nginx config:**
```bash
sudo nano /etc/nginx/sites-available/emteegee
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/emteegee/emteegee;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/emteegee/emteegee/emteegee.sock;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/emteegee /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### ⚙️ Step 5: Configure Gunicorn Service

**Create systemd service file:**
```bash
sudo nano /etc/systemd/system/emteegee.service
```

**Service configuration:**
```ini
[Unit]
Description=EMTeeGee Django Application
After=network.target

[Service]
Type=notify
User=emteegee
Group=emteegee
RuntimeDirectory=emteegee
WorkingDirectory=/home/emteegee/emteegee
Environment=PATH=/home/emteegee/emteegee/venv/bin
EnvironmentFile=/home/emteegee/emteegee/.env
ExecStart=/home/emteegee/emteegee/venv/bin/gunicorn --workers 2 --bind unix:/home/emteegee/emteegee/emteegee.sock emteegee.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl start emteegee
sudo systemctl enable emteegee
sudo systemctl status emteegee
```

### 🔒 Step 6: Setup SSL Certificate

**If using a domain:**
```bash
sudo certbot --nginx -d yourdomain.com
```

**If using IP only:**
```bash
# Create self-signed certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```

### 🧪 Step 7: Test Deployment

**Test API endpoints:**
```bash
# Test registration endpoint
curl -X POST https://yourdomain.com/api/swarm/register \
  -H "Content-Type: application/json" \
  -d '{"worker_id": "test-worker", "capabilities": {}}'

# Test work endpoint
curl -X POST https://yourdomain.com/api/swarm/get_work \
  -H "Content-Type: application/json" \
  -d '{"worker_id": "test-worker", "max_tasks": 1}'
```

### 🔄 Step 8: Update Your Workers

**Update your `.env` file:**
```bash
DJANGO_API_BASE_URL=https://yourdomain.com
```

**Test worker connection:**
```bash
python universal_worker.py
```

### 📊 Step 9: Monitoring & Maintenance

**Useful commands:**
```bash
# Check service status
sudo systemctl status emteegee nginx

# View logs
sudo journalctl -u emteegee -f
tail -f /var/log/nginx/access.log

# Update application
cd /home/emteegee/emteegee
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
sudo systemctl restart emteegee
```

### 🚨 Troubleshooting

**Common issues:**
- **502 Bad Gateway**: Check Gunicorn service status
- **Permission denied**: Check file ownership and permissions
- **SSL issues**: Verify certificate installation
- **MongoDB connection**: Check Atlas whitelist (allow all IPs: 0.0.0.0/0)

**Debug steps:**
```bash
# Check Django directly
cd /home/emteegee/emteegee
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Check Gunicorn manually
gunicorn --bind 0.0.0.0:8000 emteegee.wsgi:application
```

### ✅ Success Indicators

- [ ] Django serves at your domain/IP
- [ ] API endpoints respond correctly
- [ ] SSL certificate works (green padlock)
- [ ] Workers can register and get tasks
- [ ] systemd services auto-restart
- [ ] Nginx serves static files

Your Magic card analysis system is now production-ready! 🎉
