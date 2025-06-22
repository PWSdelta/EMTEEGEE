#!/usr/bin/env python
"""
Debug component model assignments.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.ollama_client import ALL_COMPONENT_TYPES, OLLAMA_MODELS, COMPONENT_MODEL_MAP

print("🔍 Component Assignment Analysis")
print("=" * 50)

print(f"📊 Total expected components: {len(ALL_COMPONENT_TYPES)}")
print(f"📊 Total assigned components: {len(COMPONENT_MODEL_MAP)}")
print()

# Show all expected components
print("📋 All Expected Components:")
for i, component in enumerate(ALL_COMPONENT_TYPES, 1):
    print(f"  {i:2d}. {component}")
print()

# Show model assignments
print("🤖 Model Assignments:")
for model, config in OLLAMA_MODELS.items():
    print(f"  {model} ({len(config['components'])} components):")
    for component in config['components']:
        print(f"    - {component}")
print()

# Find missing assignments
assigned_components = set(COMPONENT_MODEL_MAP.keys())
expected_components = set(ALL_COMPONENT_TYPES)

missing_components = expected_components - assigned_components
extra_components = assigned_components - expected_components

if missing_components:
    print("❌ CRITICAL: Missing Component Assignments:")
    for component in sorted(missing_components):
        print(f"  - {component}")
else:
    print("✅ All components have model assignments")

if extra_components:
    print("\n⚠️ Extra Component Assignments:")
    for component in sorted(extra_components):
        print(f"  - {component}")

print(f"\n📊 Summary:")
print(f"  Expected: {len(expected_components)} components")
print(f"  Assigned: {len(assigned_components)} components") 
print(f"  Missing: {len(missing_components)} components")
print(f"  Extra: {len(extra_components)} components")
