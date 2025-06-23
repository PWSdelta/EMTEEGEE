#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

def debug_actual_response():
    print("=== DEBUGGING ACTUAL VIEW RESPONSE ===")
    
    from cards.views import art_gallery
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/gallery/')
    
    response = art_gallery(request)
    content = response.content.decode('utf-8')
    
    print(f"Response status: {response.status_code}")
    print(f"Content length: {len(content)}")
    
    # Split content into lines for analysis
    lines = content.split('\n')
    
    # Find lines with key information
    gallery_cards_if_lines = []
    empty_gallery_lines = []
    carousel_lines = []
    stats_lines = []
    
    for i, line in enumerate(lines):
        if 'gallery_cards' in line and ('if' in line or 'else' in line):
            gallery_cards_if_lines.append((i, line.strip()))
        if 'Gallery is currently empty' in line:
            empty_gallery_lines.append((i, line.strip()))
        if 'carousel-item' in line:
            carousel_lines.append((i, line.strip()))
        if 'AI-Analyzed Cards' in line or 'Total Cards' in line:
            stats_lines.append((i, line.strip()))
    
    print(f"\n=== TEMPLATE CONDITION LINES ===")
    for line_num, line in gallery_cards_if_lines:
        print(f"Line {line_num}: {line}")
    
    print(f"\n=== EMPTY GALLERY LINES ===")
    for line_num, line in empty_gallery_lines:
        print(f"Line {line_num}: {line}")
    
    print(f"\n=== CAROUSEL ITEM LINES ===")
    for line_num, line in carousel_lines[:5]:  # Show first 5
        print(f"Line {line_num}: {line}")
    
    print(f"\n=== STATS LINES ===")
    for line_num, line in stats_lines:
        print(f"Line {line_num}: {line}")
    
    # Check if both sections exist
    if empty_gallery_lines and carousel_lines:
        print(f"\n⚠️  BOTH empty gallery message AND carousel items found!")
        print("This suggests template logic might be broken or context is inconsistent.")
        
        # Let's look at the context around the template conditions
        for line_num, line in gallery_cards_if_lines:
            print(f"\nContext around line {line_num}:")
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 4)
            for i in range(start, end):
                marker = " >>> " if i == line_num else "     "
                print(f"{marker}{i}: {lines[i].rstrip()}")
    
    # Let's also check if there are any obvious template errors
    error_indicators = ['TemplateSyntaxError', 'TemplateDoesNotExist', 'KeyError', 'NameError']
    for indicator in error_indicators:
        if indicator in content:
            print(f"\n❌ Found template error indicator: {indicator}")
    
    # Check if there are comments that might give us clues
    comment_lines = [line for line in lines if '<!--' in line and '-->' in line]
    if comment_lines:
        print(f"\n=== HTML COMMENTS ===")
        for comment in comment_lines[:5]:
            print(comment.strip())

if __name__ == "__main__":
    debug_actual_response()
