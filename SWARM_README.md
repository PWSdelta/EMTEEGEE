# 🐝 AI Analysis Swarm System

A distributed AI analysis system for Magic: The Gathering cards that intelligently distributes work across multiple machines based on their hardware capabilities.

## 🎯 System Overview

The swarm system allows you to use multiple computers to generate comprehensive AI analysis for MTG cards:

- **Desktop (RTX 3070, 64GB RAM)**: Handles fast GPU-accelerated components
- **Laptop (128GB RAM, Big CPU)**: Handles deep analysis with large models
- **Central Server**: Manages work distribution and result collection

## 📋 Components Generated

### 🔥 GPU-Optimized (Desktop)
- `play_tips` - Practical gameplay advice
- `mulligan_considerations` - Hand evaluation guidance
- `rules_clarifications` - Complex rule interactions
- `combo_suggestions` - Synergy recommendations
- `format_analysis` - Performance across formats
- `competitive_analysis` - Tournament viability
- `tactical_analysis` - Strategic depth

### 🧠 CPU-Intensive (Laptop)
- `thematic_analysis` - Lore and flavor analysis
- `historical_context` - MTG history and impact
- `art_flavor_analysis` - Artistic elements
- `design_philosophy` - Game design principles
- `advanced_interactions` - Complex rule scenarios
- `meta_positioning` - Competitive positioning

### ⚖️ Balanced (Either Machine)
- `budget_alternatives` - Cost-effective substitutions
- `deck_archetypes` - Suitable deck types
- `new_player_guide` - Beginner explanations
- `sideboard_guide` - Tournament sideboarding
- `power_level_assessment` - Card power analysis
- `investment_outlook` - Financial considerations

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
python setup_swarm.py

# Start Redis (optional but recommended)
redis-server

# Start Django server
python manage.py runserver
```

### 2. Start Workers
```bash
# Desktop worker (RTX 3070)
python desktop_worker.py http://your-server:8000

# Laptop worker (128GB RAM)
python laptop_worker.py http://your-server:8000
```

### 3. Monitor System
```bash
# Interactive dashboard
python swarm_dashboard.py --interactive

# Single status check
python swarm_dashboard.py
```

## 🔧 Configuration

### Worker Capabilities
Workers auto-detect their hardware and register appropriate capabilities:

```python
# Desktop capabilities
{
    'gpu_available': True,
    'ram_gb': 64,
    'worker_type': 'desktop',
    'preferred_models': ['llama-3.1-8b', 'phi-3-medium']
}

# Laptop capabilities  
{
    'gpu_available': False,
    'ram_gb': 128,
    'worker_type': 'laptop', 
    'preferred_models': ['mixtral-8x7b', 'llama-2-70b']
}
```

### Work Distribution
The system intelligently routes work based on:
- Available hardware (GPU/CPU)
- RAM capacity
- Worker specialization
- Current workload

## 📊 API Endpoints

### Worker Registration
```
POST /api/swarm/register
{
    "worker_id": "desktop-hostname",
    "capabilities": {...}
}
```

### Get Work
```
POST /api/swarm/get_work
{
    "worker_id": "desktop-hostname",
    "max_tasks": 2
}
```

### Submit Results
```
POST /api/swarm/submit_results
{
    "worker_id": "desktop-hostname",
    "task_id": "uuid",
    "results": {
        "components": {...},
        "execution_time": 45.2,
        "model_info": {...}
    }
}
```

## 📈 Performance Expectations

### Desktop (GPU) Performance
- **Speed**: 2-5 seconds per component
- **Throughput**: 10-20 components per minute
- **Components**: Fast, tactical analysis

### Laptop (CPU) Performance  
- **Speed**: 30-120 seconds per component
- **Throughput**: 1-2 components per minute
- **Components**: Deep, nuanced analysis

## 🎛️ Management

### Dashboard Features
- Real-time worker status
- Task completion monitoring
- Component completion rates
- Performance metrics
- Worker health checks

### Queue Management
- Automatic work distribution
- Intelligent component routing
- Failed task retry logic
- Load balancing

## 🔄 Scaling

The system can easily scale by:
1. Adding more worker machines
2. Configuring hardware-specific routing
3. Implementing priority queues
4. Adding specialized model types

## 🛠️ Customization

### Adding New Components
1. Define component in `SwarmManager.COMPONENT_TYPES`
2. Add routing logic in `_get_worker_components()`
3. Implement generation in worker scripts
4. Update dashboard monitoring

### Model Integration
Replace the placeholder analysis generation with your actual LLM inference:
- Ollama integration
- Transformers library
- API-based models
- Custom inference servers

## 🐛 Troubleshooting

### Common Issues
- **Redis connection**: System works without Redis but queuing is less efficient
- **Worker registration**: Check network connectivity to Django server
- **Task timeouts**: Large models may need longer timeout values
- **Memory issues**: Monitor RAM usage on CPU-intensive tasks

### Logs
- Worker logs: Console output with timestamps
- Server logs: Django logs in `logs/` directory  
- Task logs: MongoDB `swarm_tasks` collection

This system transforms your multi-machine setup into a powerful distributed AI analysis engine, maximizing the value of your existing hardware!
