# EMTEEGEE - Magic: The Gathering AI Analysis System

🎯 **A distributed AI-powered platform for analyzing Magic: The Gathering cards**

## Quick Start

```bash
# Local development
git clone https://github.com/yourusername/emteegee.git
cd emteegee
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python manage.py runserver 8001
```

## Features

- **AI Card Analysis** - 20 component types per card
- **Distributed Processing** - Swarm workers for scalability  
- **Web Interface** - Beautiful card gallery and search
- **EDHREC Integration** - Priority-based processing
- **Production Ready** - VPS deployment for $5/month

## Documentation

📖 **[Complete Documentation](claude/README.md)** - Setup, deployment, troubleshooting

🔄 **[Swarm System Guide](ENHANCED_SWARM_GUIDE.md)** - Distributed worker details

## Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Web Client    │    │    Django    │    │   MongoDB       │
│   (Browser)     │◄──►│   Server     │◄──►│   Atlas         │
└─────────────────┘    └──────┬───────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Swarm Workers   │
                    │  (Desktop/VPS)   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Ollama AI      │
                    │   (Local LLM)    │
                    └──────────────────┘
```

## Status

✅ **Core System** - Fully functional  
✅ **Web Interface** - Cards display and navigation working  
✅ **Swarm Processing** - Distributed workers operational  
✅ **Production Ready** - VPS deployment tested  

---

🚀 **Ready to analyze the entire Magic: The Gathering card universe!**

See [claude/README.md](claude/README.md) for complete documentation.
