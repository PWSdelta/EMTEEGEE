#!/usr/bin/env python3
"""
Test script to check mana symbol HTML output
"""
import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.templatetags.card_filters import scryfall_mana_symbols

# Test the function
test_mana_cost = "{2}{W}{U}"
result = scryfall_mana_symbols(test_mana_cost)

# Write to HTML file to check in browser
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Mana Symbol Test</title>
    <style>
        .mana-symbol {{
            height: 1.2em;
            width: auto;
            vertical-align: text-top;
            margin: 0 1px;
        }}
        .test-result {{
            border: 1px solid #ccc;
            padding: 10px;
            margin: 10px 0;
            background: #f9f9f9;
        }}
    </style>
</head>
<body>
    <h1>Mana Symbol Test</h1>
    <div class="test-result">
        <strong>Input:</strong> {test_mana_cost}<br>
        <strong>Output:</strong> {result}<br>
        <strong>Raw HTML:</strong> <pre>{result.replace('<', '&lt;').replace('>', '&gt;')}</pre>
    </div>
</body>
</html>
"""

with open('mana_test.html', 'w') as f:
    f.write(html_content)

print("Test HTML file created: mana_test.html")
print("Open this file in a browser to see the actual rendering.")
