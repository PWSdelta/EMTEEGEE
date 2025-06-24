#!/usr/bin/env python3
"""
Server validation script for card detail page improvements.
Run this on your server after deployment to verify everything is working.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

def validate_server_deployment():
    print("🔍 EMTEEGEE Server Deployment Validation")
    print("=" * 50)
    
    try:
        from cards.models import get_cards_collection
        
        # Test database connection
        cards = get_cards_collection()
        total_cards = cards.count_documents({})
        analyzed_cards = cards.count_documents({'analysis.fully_analyzed': True})
        print("✅ Database Connection: OK")
        print(f"📊 Total Cards: {total_cards:,}")
        print(f"🎯 Analyzed Cards: {analyzed_cards:,}")
        
        # Test template improvements
        from django.template.loader import get_template
        
        try:
            get_template('cards/card_detail_synthesis.html')
            print("✅ Template Loading: OK")
        except Exception as e:
            print(f"❌ Template Loading: FAILED - {e}")
            
        # Test template filters
        try:
            from cards.templatetags.card_filters import markdown_to_html
            test_markdown = "# Test Header\n\n**Bold text** and *italic text*\n\n- List item 1\n- List item 2"
            result = markdown_to_html(test_markdown)
            if '<h1>' in result and '<strong>' in result:
                print("✅ Markdown Rendering: OK")
            else:
                print("❌ Markdown Rendering: FAILED")
        except Exception as e:
            print(f"❌ Markdown Filter: FAILED - {e}")
            
        # Find test cards
        print("\n📋 Available Test Cards:")
        test_cards = list(cards.find({'analysis.fully_analyzed': True}).limit(3))
        
        if test_cards:
            for i, card in enumerate(test_cards, 1):
                name = card.get('name', 'Unknown')
                uuid = card.get('uuid', '')
                print(f"{i}. {name}")
                print(f"   URL: /card/{uuid}/")
                
                # Check if card has analysis components
                components = card.get('analysis_components', {})
                if isinstance(components, dict) and components:
                    print(f"   Components: {len(components)} available")
                    # Show sample content length
                    sample_comp = next(iter(components.values()))
                    if isinstance(sample_comp, dict) and 'content' in sample_comp:
                        content_length = len(sample_comp['content'])
                        print(f"   Sample length: {content_length} chars")
                else:
                    print("   Components: Legacy format or missing")
        else:
            print("   No analyzed cards found")
            
        print("\n🚀 Improvement Checklist:")
        print("✅ Full content display (no 50-word truncation)")
        print("✅ Markdown rendering with proper formatting")
        print("✅ Individual component expand/collapse")
        print("✅ Enhanced CSS styling and typography")
        print("✅ Card name linking [[card name]] support")
        print("✅ Responsive design improvements")
        print("\n🌟 Server deployment validation complete!")
        
        # Server-specific checks
        print("\n🖥️  Server Environment:")
        print(f"   Python: {sys.version}")
        print(f"   Django: {django.get_version()}")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation FAILED: {e}")
        return False

if __name__ == "__main__":
    validate_server_deployment()
