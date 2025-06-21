# EMTEEGEE Core Card Review System
## Essential Guide for Claude 4.0 Django Implementation

**Purpose:** Recreate the AI-powered MTG card analysis system in Django  
**Core Feature:** Generate 20 analysis components per card using 4 Ollama models

---

## 1. System Overview

EMTEEGEE generates comprehensive card analyses using local Ollama models. Each card gets 20 different analysis components, and the `fully_analyzed` flag is set to `True` only when all 20 components exist.

**Key Concepts:**
- **4 AI Models** - Different perspectives for different analysis types
- **20 Components** - Comprehensive coverage of each card
- **Job System** - Background processing for bulk generation
- **Quality Control** - Validation and retry logic

---

## 2. The Four Ollama Models

```python
OLLAMA_MODELS = {
    'llama3.2:latest': {
        'use_case': 'Quick analysis, play tips, rules clarifications',
        'components': ['play_tips', 'mulligan_considerations', 'rules_clarifications']
    },
    'llama3.1:latest': {
        'use_case': 'Balanced analysis, synergies, competitive play',
        'components': ['thematic_analysis', 'synergy_analysis', 'competitive_analysis', 
                      'format_analysis', 'deck_archetypes', 'sideboard_guide']
    },
    'llama3.3:70b': {
        'use_case': 'Deep analysis, complex interactions, investment',
        'components': ['tactical_analysis', 'power_level_assessment', 'meta_positioning',
                      'investment_outlook', 'advanced_interactions']
    },
    'mistral:7b': {
        'use_case': 'Alternative perspective, budget options, education',
        'components': ['budget_alternatives', 'historical_context', 'new_player_guide',
                      'design_philosophy']
    }
}
```

---

## 3. The 20 Analysis Components

Each component provides a different angle on the card:

### Strategic Components (6)
1. **tactical_analysis** - Deep mechanical breakdown (llama3.3:70b)
2. **power_level_assessment** - Overall power evaluation (llama3.3:70b)
3. **competitive_analysis** - Tournament viability (llama3.1:latest)
4. **synergy_analysis** - Card interactions (llama3.1:latest)
5. **meta_positioning** - Current metagame role (llama3.3:70b)
6. **advanced_interactions** - Complex rules scenarios (llama3.3:70b)

### Practical Components (6)
7. **play_tips** - Practical usage advice (llama3.2:latest)
8. **combo_suggestions** - Synergistic cards (llama3.1:latest)
9. **format_analysis** - Performance across formats (llama3.1:latest)
10. **deck_archetypes** - Suitable deck types (llama3.1:latest)
11. **mulligan_considerations** - Keep/mulligan decisions (llama3.2:latest)
12. **sideboard_guide** - Sideboarding strategies (llama3.1:latest)

### Educational Components (4)
13. **new_player_guide** - Beginner explanations (mistral:7b)
14. **rules_clarifications** - Common rules questions (llama3.2:latest)
15. **budget_alternatives** - Cheaper similar cards (mistral:7b)
16. **historical_context** - MTG history perspective (mistral:7b)

### Thematic Components (4)
17. **thematic_analysis** - Lore and flavor (llama3.1:latest)
18. **art_flavor_analysis** - Artistic elements (llama3.1:latest)
19. **design_philosophy** - Design intent (mistral:7b)
20. **investment_outlook** - Financial/collectible value (llama3.3:70b)

---

## 4. Database Schema (Django Models)

```python
class Card(models.Model):
    name = models.CharField(max_length=200)
    scryfall_id = models.UUIDField(unique=True)
    # ... other card fields ...
    
    # Analysis tracking
    fully_analyzed = models.BooleanField(default=False)  # TRUE when all 20 exist
    component_count = models.IntegerField(default=0)
    analysis_completed_at = models.DateTimeField(null=True)

class ReviewComponent(models.Model):
    COMPONENT_TYPES = [
        ('tactical_analysis', 'Tactical Analysis'),
        ('thematic_analysis', 'Thematic Analysis'),
        # ... all 20 types
    ]
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    component_type = models.CharField(max_length=50, choices=COMPONENT_TYPES)
    content_markdown = models.TextField()
    model_used = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['card', 'component_type']
```

---

## 5. Ollama API Integration

```python
import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate_component(self, card, component_type):
        model = OLLAMA_MODELS[component_type]['model']
        prompt = self.build_prompt(card, component_type)
        
        response = requests.post(f"{self.base_url}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "system": "You are an expert MTG analyst. Write detailed, accurate analysis.",
            "stream": False,
            "options": {"temperature": 0.7}
        })
        
        return response.json()["response"]
    
    def build_prompt(self, card, component_type):
        base_context = f"""
Card: {card.name}
Mana Cost: {card.mana_cost}
Type: {card.type_line}
Text: {card.oracle_text}
"""
        
        prompts = {
            'tactical_analysis': f"{base_context}\nProvide deep tactical analysis with specific play patterns and timing.",
            'play_tips': f"{base_context}\nGive 3-4 practical tips for playing this card effectively.",
            'thematic_analysis': f"{base_context}\nAnalyze the lore, flavor, and thematic elements.",
            # ... specific prompts for each component type
        }
        
        return prompts.get(component_type, base_context)
```

---

## 6. Job System Architecture

### Background Tasks (Celery)
```python
@shared_task
def generate_single_component(card_id, component_type):
    """Generate one component for a card"""
    card = Card.objects.get(id=card_id)
    client = OllamaClient()
    
    content = client.generate_component(card, component_type)
    
    ReviewComponent.objects.update_or_create(
        card=card,
        component_type=component_type,
        defaults={
            'content_markdown': content,
            'model_used': OLLAMA_MODELS[component_type]['model'],
            'is_active': True
        }
    )
    
    # Update card status
    card.component_count = card.components.filter(is_active=True).count()
    card.fully_analyzed = card.component_count >= 20
    if card.fully_analyzed:
        card.analysis_completed_at = timezone.now()
    card.save()

@shared_task
def analyze_card_completely(card_id):
    """Generate all 20 components for a card"""
    component_types = [
        'tactical_analysis', 'thematic_analysis', 'play_tips',
        'combo_suggestions', 'power_level_assessment', 'format_analysis',
        'synergy_analysis', 'competitive_analysis', 'budget_alternatives',
        'historical_context', 'art_flavor_analysis', 'investment_outlook',
        'deck_archetypes', 'meta_positioning', 'new_player_guide',
        'advanced_interactions', 'mulligan_considerations', 'sideboard_guide',
        'rules_clarifications', 'design_philosophy'
    ]
    
    for component_type in component_types:
        generate_single_component.delay(card_id, component_type)
```

### Job Management
```python
def queue_cards_for_analysis(card_ids):
    """Queue multiple cards for complete analysis"""
    for card_id in card_ids:
        analyze_card_completely.delay(card_id)
    
    return f"Queued {len(card_ids)} cards for analysis"

def get_analysis_progress():
    """Check overall analysis progress"""
    total_cards = Card.objects.count()
    fully_analyzed = Card.objects.filter(fully_analyzed=True).count()
    
    return {
        'total_cards': total_cards,
        'fully_analyzed': fully_analyzed,
        'completion_percentage': (fully_analyzed / total_cards * 100) if total_cards > 0 else 0
    }
```

---

## 7. Key Implementation Points

### Component Generation Flow
1. **Card Selected** - Choose card for analysis
2. **Queue 20 Tasks** - One task per component type
3. **Generate Content** - Use appropriate Ollama model
4. **Save Component** - Store in ReviewComponent table
5. **Update Status** - Set `fully_analyzed=True` when count reaches 20

### Quality Control
- Each component validated for minimum word count
- Retry logic for failed generations
- Model-specific prompts for consistent output
- Manual review capability through admin interface

### Performance Considerations
- Background processing prevents UI blocking
- Model routing based on complexity
- Caching for frequently accessed components
- Progress tracking for long-running operations

---

## 8. Django Views Integration

```python
def card_detail(request, card_id):
    """Display card with all available components"""
    card = get_object_or_404(Card, id=card_id)
    components = card.components.filter(is_active=True).order_by('component_type')
    
    context = {
        'card': card,
        'components': components,
        'fully_analyzed': card.fully_analyzed,
        'progress': f"{card.component_count}/20 components"
    }
    return render(request, 'cards/detail.html', context)

def trigger_analysis(request, card_id):
    """Start analysis for a specific card"""
    if request.method == 'POST':
        analyze_card_completely.delay(card_id)
        messages.success(request, 'Analysis started for this card')
    return redirect('card_detail', card_id=card_id)
```

---

## Summary

The MagicAI system generates comprehensive card analyses through:
- **4 specialized Ollama models** for different analysis perspectives
- **20 distinct components** covering all aspects of each card
- **Background job system** for scalable processing
- **Quality control** with validation and retry logic
- **Progress tracking** via the `fully_analyzed` flag

The system is designed to be rebuilt in Django with modern practices while maintaining the core AI analysis capabilities.
