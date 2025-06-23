#!/usr/bin/env python3
"""
UUID/ID Field Compatibility Fix for Enhanced Swarm Manager
This script fixes the enhanced_swarm_manager.py to handle both 'uuid' and 'id' fields
"""

import re

def fix_enhanced_swarm_manager():
    file_path = 'cards/enhanced_swarm_manager.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the card['uuid'] issue in priority cache building
    old_pattern = r"""priority_updates\.append\(\{
                'card_uuid': card\['uuid'\],
                'priority_score': priority_score,
                'last_updated': datetime\.now\(timezone\.utc\)
            \}\)"""
    
    new_code = """# Handle both 'uuid' and 'id' fields for card identification
            card_id = card.get('uuid') or card.get('id') or str(card.get('_id'))
            if not card_id:
                enhanced_swarm_logger.error(f"Card missing identification field: {card.get('name', 'Unknown')}")
                continue
            priority_updates.append({
                'card_uuid': card_id,
                'priority_score': priority_score,
                'last_updated': datetime.now(timezone.utc)
            })"""
    
    # Find and replace the problematic line
    if "'card_uuid': card['uuid']," in content:
        content = content.replace(
            "priority_updates.append({\n                'card_uuid': card['uuid'],\n                'priority_score': priority_score,\n                'last_updated': datetime.now(timezone.utc)\n            })",
            "# Handle both 'uuid' and 'id' fields for card identification\n            card_id = card.get('uuid') or card.get('id') or str(card.get('_id'))\n            if not card_id:\n                enhanced_swarm_logger.error(f\"Card missing identification field: {card.get('name', 'Unknown')}\")\n                continue\n            priority_updates.append({\n                'card_uuid': card_id,\n                'priority_score': priority_score,\n                'last_updated': datetime.now(timezone.utc)\n            })"
        )
        print("✅ Fixed priority cache card UUID issue")
    
    # Add 'id' field to MongoDB projection
    if "'uuid': 1, 'name': 1, 'edhrecRank': 1" in content:
        content = content.replace(
            "'uuid': 1, 'name': 1, 'edhrecRank': 1",
            "'uuid': 1, 'id': 1, 'name': 1, 'edhrecRank': 1"
        )
        print("✅ Added 'id' field to MongoDB projection")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Enhanced Swarm Manager fixed for UUID/ID field compatibility")

if __name__ == '__main__':
    fix_enhanced_swarm_manager()
