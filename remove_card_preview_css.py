#!/usr/bin/env python
"""
Remove card preview modal CSS
"""
import re

css_file = "c:/Users/Owner/Code/emteegee/static/css/emteegee.css"

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the card preview modal section
# It starts with "/* Card Preview Modal */" and ends with "/* Responsive Design */"
start_marker = "/* Card Preview Modal */"
end_marker = "/* Responsive Design */"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # Remove the card preview section
    new_content = content[:start_idx] + content[end_idx:]
    
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Removed card preview modal CSS")
    print(f"   Removed {end_idx - start_idx} characters")
else:
    print("❌ Could not find card preview section markers")
    print(f"   Start marker found: {start_idx != -1}")
    print(f"   End marker found: {end_idx != -1}")
