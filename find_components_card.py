import os

# Read the models file to see what's in it
models_path = r'C:\Users\Owner\Code\emteegee\cards\models.py'
print(f"Reading {models_path}")
print("-" * 50)

with open(models_path, 'r') as f:
    content = f.read()
    print(content)