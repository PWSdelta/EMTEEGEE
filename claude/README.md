# EMTEEGEE - Magic: The Gathering AI Analysis System

**A distributed AI-powered Magic card analysis platform with swarm processing capabilities.**

## 🚀 Quick Start

### Local Development
```bash
# Clone and setup
git clone https://github.com/yourusername/emteegee.git
cd emteegee
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB connection and settings

# Run locally
python manage.py runserver 8001
```

### Production Deployment (VPS)
```bash
# 1. Create Linode server (Ubuntu 22.04, $5/month)
ssh root@YOUR_SERVER_IP

# 2. Run deployment script
curl -sSL https://raw.githubusercontent.com/yourusername/emteegee/main/claude/scripts/full_deploy.sh | bash

# 3. Setup domain and SSL
sudo certbot --nginx -d yourdomain.com
```

## 🏗️ Architecture

**Core Components:**
- **Django Web Server** - Main application, API endpoints, web interface
- **MongoDB Atlas** - Card data and analysis storage  
- **Swarm Workers** - Distributed AI analysis processing
- **Ollama AI** - Local language models for card analysis

**Processing Flow:**
1. Cards imported from Scryfall API
2. EDHREC priority system queues cards for analysis
3. Distributed workers pull work from server
4. AI analyzes cards with 20 component types
5. Results stored and displayed in web interface

## � Features

### Card Analysis
- **20 AI Components** per card (tactics, synergies, power level, etc.)
- **EDHREC Integration** for popularity-based prioritization
- **Comprehensive Coverage** of Magic card database
- **Real-time Processing** with distributed workers

### Web Interface
- **Card Gallery** - Browse analyzed cards with beautiful UI
- **Search & Filter** - Find cards by various criteria  
- **Analysis Dashboard** - Monitor processing progress
- **The Abyss** - Comprehensive card database view

### Swarm System
- **Universal Workers** - Run analysis on any machine
- **Load Balancing** - Automatic work distribution
- **Fault Tolerance** - Handles worker disconnections
- **Progress Tracking** - Real-time status monitoring

## 🛠️ Configuration

### Environment Variables (.env)
```bash
# MongoDB
MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/emteegee?retryWrites=true&w=majority

# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_API_BASE_URL=https://yourdomain.com

# Ollama (optional)
OLLAMA_HOST=http://localhost:11434

# Swarm
SWARM_SERVER_URL=http://yourdomain.com
```

### Worker Setup
```bash
# On any machine (desktop, laptop, etc.)
git clone https://github.com/yourusername/emteegee.git
cd emteegee
pip install -r requirements.txt

# Configure worker
cp .env.example .env
# Set SWARM_SERVER_URL to your production server

# Run worker
python universal_worker_enhanced.py
```

## 🔧 Management Commands

### Development
```bash
# Import cards from Scryfall
python setup_scryfall.py

# Setup EDHREC prioritization  
python setup_edhrec_prioritization.py

# Run swarm manager
python swarm_manager.py

# Check system status
python manage.py shell
```

### Production
```bash
# Deploy updates
/home/emteegee/deploy.sh

# Service management
sudo systemctl status emteegee nginx
sudo systemctl restart emteegee

# View logs
sudo journalctl -u emteegee -f
sudo tail -f /var/log/nginx/emteegee_access.log

# Backup data
/home/emteegee/backup.sh
```

## 📈 Performance

**Expected Capacity:**
- 10+ concurrent workers
- Hundreds of API calls/minute
- 99.9% uptime
- <200ms API response times

**Resource Usage:**
- VPS: 1GB RAM, 1 CPU core ($5/month)
- Worker: Minimal resources, scales horizontally
- Storage: <5GB for full card database

## 🆘 Troubleshooting

### Common Issues
```bash
# Server not responding
sudo systemctl status emteegee nginx

# Database connection issues  
python manage.py shell
# Test MongoDB connection

# Worker connection issues
# Check SWARM_SERVER_URL in worker .env
# Verify server API endpoints accessible

# Template/static file issues
python manage.py collectstatic --noinput
sudo systemctl restart emteegee
```

### Debug Mode
```bash
# Run Django directly for debugging
cd /path/to/emteegee
source venv/bin/activate  # if using venv
python manage.py runserver 0.0.0.0:8001

# Test specific components
python debug_card_structure.py
python simple_api_test.py
```

## 🎯 Success Criteria

✅ **Core Functionality:**
- [ ] Web interface loads and displays cards
- [ ] API endpoints respond correctly
- [ ] Workers can connect and process cards
- [ ] Analysis results stored in database

✅ **Production Ready:**
- [ ] HTTPS/SSL working (green padlock)
- [ ] Services auto-restart after reboot  
- [ ] Logs rotating properly
- [ ] Backups running automatically

✅ **Performance:**
- [ ] Multiple workers processing concurrently
- [ ] Response times under targets
- [ ] No memory leaks or resource issues

## 📚 Documentation Files

**Keep These:**
- `README.md` (this file) - Main documentation
- `ENHANCED_SWARM_GUIDE.md` - Detailed swarm system docs
- `scripts/` - Deployment automation

**Archive/Remove:**
- Multiple overlapping roadmaps and status files
- Duplicate technical summaries  
- Outdated development insights

---

🎉 **You now have a professional Magic card analysis platform running for $5/month!**

For detailed swarm system documentation, see `ENHANCED_SWARM_GUIDE.md`.
For deployment scripts, see the `scripts/` directory.
