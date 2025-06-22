# EMTeeGee Documentation Hub
## Complete VPS Deployment Documentation

### 📚 Available Guides

1. **[VPS Deployment Plan](VPS_DEPLOYMENT_PLAN.md)**
   - Architecture overview
   - Cost breakdown ($5/month)
   - Performance expectations
   - Technology stack

2. **[VPS Setup Guide](VPS_SETUP_GUIDE.md)**
   - Step-by-step server setup
   - Django configuration
   - Nginx and SSL setup
   - Testing and troubleshooting

3. **[Deployment Scripts](scripts/)**
   - `initial_setup.sh` - Server initialization
   - `django_setup.sh` - Django application setup
   - `configure_services.sh` - Nginx and systemd configuration

4. **[Production Configuration]()**
   - `requirements_production.txt` - Additional Python packages
   - `settings_production.py` - Production Django settings

### 🚀 Quick Start Deployment

**1. Create Linode Server**
- Plan: Nanode 1GB ($5/month)
- OS: Ubuntu 22.04 LTS
- Add SSH key

**2. Run Initial Setup**
```bash
ssh root@YOUR_SERVER_IP
curl -sSL https://raw.githubusercontent.com/yourusername/emteegee/main/claude/scripts/initial_setup.sh | bash
```

**3. Deploy Application**
```bash
su - emteegee
git clone https://github.com/yourusername/emteegee.git
cd emteegee
./claude/scripts/django_setup.sh
```

**4. Configure Services**
```bash
sudo ./claude/scripts/configure_services.sh
```

**5. Setup SSL**
```bash
sudo certbot --nginx -d yourdomain.com
```

### 🛠️ Features Included

**Server Configuration:**
- ✅ Nginx reverse proxy
- ✅ Gunicorn WSGI server
- ✅ systemd service management
- ✅ SSL certificate (Let's Encrypt)
- ✅ Firewall configuration
- ✅ Automatic backups
- ✅ Log rotation

**Security:**
- ✅ HTTPS enforcement
- ✅ Security headers
- ✅ Firewall rules
- ✅ File permissions
- ✅ Process isolation

**Monitoring:**
- ✅ Application logs
- ✅ Nginx access logs
- ✅ Health check endpoints
- ✅ Service status monitoring

**Maintenance:**
- ✅ Deployment script
- ✅ Backup script
- ✅ Log rotation
- ✅ Auto-restart services

### 📊 Expected Performance

**Response Times:**
- API registration: <100ms
- Work requests: <200ms
- Result submission: <300ms

**Capacity:**
- 10+ concurrent workers
- Hundreds of API calls/minute
- 99.9% uptime

**Resource Usage:**
- RAM: ~300-500MB
- CPU: Low utilization
- Storage: <5GB

### 🔧 Maintenance Commands

**Service Management:**
```bash
# Check status
sudo systemctl status emteegee nginx

# Restart services
sudo systemctl restart emteegee
sudo systemctl reload nginx

# View logs
sudo journalctl -u emteegee -f
sudo tail -f /var/log/nginx/emteegee_access.log
```

**Application Updates:**
```bash
# Quick deployment
/home/emteegee/deploy.sh

# Manual deployment
cd /home/emteegee/emteegee
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput
sudo systemctl restart emteegee
```

**Backups:**
```bash
# Manual backup
/home/emteegee/backup.sh

# View backups
ls -la /home/emteegee/backups/
```

### 🆘 Troubleshooting

**Common Issues:**
- 502 Bad Gateway → Check Gunicorn service
- Permission errors → Check file ownership
- SSL issues → Verify certificate
- MongoDB connection → Check Atlas whitelist

**Debug Commands:**
```bash
# Test Django directly
cd /home/emteegee/emteegee
source venv/bin/activate
python manage.py check
python manage.py runserver 0.0.0.0:8000

# Test Gunicorn
gunicorn --bind 0.0.0.0:8000 emteegee.wsgi:application

# Check service logs
sudo journalctl -u emteegee --no-pager -l
```

### 🎯 Success Criteria

- [ ] Server accessible via domain/IP
- [ ] API endpoints respond correctly
- [ ] SSL certificate working (green padlock)
- [ ] Universal workers can connect
- [ ] Services auto-restart after reboot
- [ ] Static files served by Nginx
- [ ] Logs rotating properly
- [ ] Backups running daily

### 💡 Next Steps

After successful deployment:

1. **Update Workers**: Change `.env` to point to your VPS
2. **Test Distributed Processing**: Run workers from desktop/laptop
3. **Monitor Performance**: Watch logs and resource usage
4. **Setup Alerts**: Configure email notifications
5. **Scale as Needed**: Upgrade server if traffic increases

Your Magic card analysis system will be production-ready and rock-solid! 🎉

### 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review service logs
3. Verify configuration files
4. Test components individually
5. Restore from backup if needed

**Remember**: This setup gives you a professional, scalable Magic card analysis platform for just $5/month! 🌟
