#!/bin/bash
# Service Configuration Script
# Creates Nginx and systemd service configurations

set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

echo "⚙️ Configuring services for EMTeeGee..."

# Get domain/IP from user
read -p "Enter your domain name or server IP: " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Domain/IP is required"
    exit 1
fi

# Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
cat > /etc/nginx/sites-available/emteegee << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Logging
    access_log /var/log/nginx/emteegee_access.log;
    error_log /var/log/nginx/emteegee_error.log;

    # Favicon
    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    # Static files
    location /static/ {
        alias /home/emteegee/emteegee/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /home/emteegee/emteegee/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/emteegee/emteegee/emteegee.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API specific optimizations
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/home/emteegee/emteegee/emteegee.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # API optimizations
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # Health check endpoint
    location /health/ {
        access_log off;
        include proxy_params;
        proxy_pass http://unix:/home/emteegee/emteegee/emteegee.sock;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/emteegee /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/emteegee.service << EOF
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
ExecStart=/home/emteegee/emteegee/venv/bin/gunicorn \\
    --user emteegee \\
    --group emteegee \\
    --bind unix:/home/emteegee/emteegee/emteegee.sock \\
    --workers 2 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --timeout 60 \\
    --keep-alive 5 \\
    --log-level info \\
    --log-file /home/emteegee/logs/gunicorn.log \\
    --access-logfile /home/emteegee/logs/gunicorn_access.log \\
    --capture-output \\
    emteegee.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable emteegee
systemctl enable nginx

# Create socket directory and set permissions
install -d -o emteegee -g emteegee /run/emteegee

# Start services
systemctl start emteegee
systemctl restart nginx

# Check service status
echo "📊 Service status:"
systemctl is-active emteegee && echo "✅ EMTeeGee service is running" || echo "❌ EMTeeGee service failed"
systemctl is-active nginx && echo "✅ Nginx is running" || echo "❌ Nginx failed"

echo ""
echo "✅ Service configuration complete!"
echo ""
echo "Next steps:"
echo "1. Test your site: http://$DOMAIN"
echo "2. Setup SSL: sudo certbot --nginx -d $DOMAIN"
echo "3. Test API endpoints"
echo ""
echo "📝 Useful commands:"
echo "  - Check service status: sudo systemctl status emteegee"
echo "  - View logs: sudo journalctl -u emteegee -f"
echo "  - Restart service: sudo systemctl restart emteegee"
echo "  - Nginx logs: sudo tail -f /var/log/nginx/emteegee_access.log"
