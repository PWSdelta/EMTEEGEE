# MagicAI Card Review System - Summary for Claude 4.0
## Django Migration Guide

**Date:** June 21, 2025  
**Purpose:** Concise guide for recreating the AI card analysis pipeline in Django + MongoDB

---

## 1. Overview

MagicAI generates comprehensive MTG card analyses using **4 Ollama models** to create **20 different component types** per card. Cards are marked `fully_analyzed=True` when all 20 components are generated.

---

## 2. The Four Ollama Models

```python
OLLAMA_MODELS = {
    'llama3.2:latest': {
        'name': 'Efficient Model',
        'use_case': 'Play tips, rules clarifications, mulligan advice',
        'components': ['play_tips', 'rules_clarifications', 'mulligan_considerations']
    },
    'llama3.1:latest': {
        'name': 'Balanced Model', 
        'use_case': 'General analysis, synergies, formats',
        'components': ['thematic_analysis', 'synergy_analysis', 'format_analysis', 
                      'deck_archetypes', 'sideboard_guide', 'art_flavor_analysis']
    },
    'llama3.3:70b': {
        'name': 'Premium Model',
        'use_case': 'Deep analysis, competitive play, complex interactions',
        'components': ['tactical_analysis', 'power_level_assessment', 'competitive_analysis',
                      'investment_outlook', 'meta_positioning', 'advanced_interactions']
    },
    'mistral:7b': {
        'name': 'Alternative Perspective',
        'use_case': 'Budget options, beginner content, historical context',
        'components': ['budget_alternatives', 'historical_context', 'new_player_guide',
                      'design_philosophy']
    }
}
```

---

## 3. The 20 Component Types

Each card gets all 20 analysis components:

### Strategic Analysis (Models: llama3.3:70b, llama3.1:latest)
- **tactical_analysis** - Deep mechanical breakdown and interactions
- **power_level_assessment** - Overall power evaluation  
- **competitive_analysis** - Viability in competitive play
- **synergy_analysis** - How it works with different strategies
- **format_analysis** - Performance across MTG formats
- **meta_positioning** - Role in current metagame

### Practical Guidance (Models: llama3.2:latest, llama3.1:latest)
- **play_tips** - Practical usage advice
- **combo_suggestions** - Cards that synergize well
- **deck_archetypes** - Deck types where it excels
- **mulligan_considerations** - When to keep/mulligan
- **sideboard_guide** - Sideboarding strategies
- **rules_clarifications** - Common rules questions

### Flavor & Context (Models: llama3.1:latest, mistral:7b)
- **thematic_analysis** - Lore and flavor elements
- **art_flavor_analysis** - Artistic and flavor text analysis
- **historical_context** - Place in MTG history
- **design_philosophy** - Design intent behind the card

### Player-Focused Content (Models: mistral:7b, llama3.3:70b)
- **new_player_guide** - Beginner-friendly explanations
- **budget_alternatives** - Cheaper similar effects
- **investment_outlook** - Financial/collectibility analysis
- **advanced_interactions** - Complex rules edge cases

---

## 4. Django Models

```python
# models.py
class Card(models.Model):
    name = models.CharField(max_length=200)
    # ... other card fields ...
    
    # Analysis Status
    fully_analyzed = models.BooleanField(default=False, db_index=True)
    component_count = models.IntegerField(default=0)
    analysis_completed_at = models.DateTimeField(null=True)

class ReviewComponent(models.Model):
    COMPONENT_CHOICES = [
        ('tactical_analysis', 'Tactical Analysis'),
        ('thematic_analysis', 'Thematic Analysis'),
        ('play_tips', 'Play Tips'),
        # ... all 20 types
    ]
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='components')
    component_type = models.CharField(max_length=50, choices=COMPONENT_CHOICES)
    content_markdown = models.TextField()
    model_used = models.CharField(max_length=50)  # Which Ollama model
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['card', 'component_type']
```

---

## 5. Job System Basics

### Card Analysis Pipeline
1. **Job Creation**: Cards queued for analysis (usually cards without `fully_analyzed=True`)
2. **Component Generation**: 20 separate tasks created per card
3. **Model Assignment**: Each component type uses its designated Ollama model
4. **Completion Check**: When all 20 components exist, card marked `fully_analyzed=True`

### Django Celery Tasks
```python
# tasks.py
@shared_task
def generate_component(card_id, component_type):
    """Generate single component using appropriate Ollama model"""
    card = Card.objects.get(id=card_id)
    model = COMPONENT_MODEL_MAP[component_type]
    
    # Call Ollama API
    content = ollama_client.generate(model, build_prompt(card, component_type))
    
    # Save component
    ReviewComponent.objects.update_or_create(
        card=card,
        component_type=component_type,
        defaults={'content_markdown': content, 'model_used': model}
    )
    
    # Update card status
    update_card_analysis_status(card)

@shared_task  
def analyze_card_completely(card_id):
    """Queue all 20 components for a card"""
    for component_type in COMPONENT_TYPES:
        generate_component.delay(card_id, component_type)

def update_card_analysis_status(card):
    """Check if card has all 20 components"""
    count = card.components.filter(is_active=True).count()
    card.component_count = count
    card.fully_analyzed = (count >= 20)
    if card.fully_analyzed:
        card.analysis_completed_at = timezone.now()
    card.save()
```

---

## 6. Ollama Integration

### Basic Client
```python
# ollama_client.py
import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, model, prompt):
        response = requests.post(f"{self.base_url}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        return response.json()["response"]
```

### Component-Specific Prompts
```python
def build_prompt(card, component_type):
    base = f"Card: {card.name}\nText: {card.oracle_text}\n"
    
    prompts = {
        'tactical_analysis': base + "Provide deep tactical analysis focusing on mechanics and timing.",
        'play_tips': base + "Give 3-4 practical tips for playing this card effectively.",
        'thematic_analysis': base + "Analyze the lore, flavor, and thematic elements.",
        # ... prompts for all 20 types
    }
    
    return prompts[component_type]
```

---

## 7. Production Workflow

### Bulk Analysis Process
1. Find cards with `fully_analyzed=False`
2. Queue analysis jobs for each card
3. Generate all 20 components using appropriate models
4. Mark cards as `fully_analyzed=True` when complete
5. Monitor progress via admin interface

### Key Flags
- **fully_analyzed**: Boolean indicating card has all 20 components
- **component_count**: Current number of active components (0-20)
- **analysis_completed_at**: Timestamp when analysis finished

---

This system creates comprehensive, multi-perspective card analyses by leveraging different AI models for their strengths, ensuring every card gets 20 distinct analysis components before being marked as complete.
