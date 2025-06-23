#!/usr/bin/env python3
"""
Enhanced Universal EMTeeGee Worker v3.0 - Enhanced Swarm Integration (CLEAN)
- Updated for enhanced swarm manager with smart prioritization
- Supports all 20 analysis components with GPU/CPU allocation
- Enhanced coherence validation and batch processing support
- Improved task tracking and state management
- Better logging and monitoring
"""

import json
import time
import requests
import socket
import platform
import psutil
import multiprocessing
import ollama
import os
import sys
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point with enhanced argument parsing"""
    # Check for server URL argument
    server_url = None
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
        print(f"Using server URL from argument: {server_url}")
    
    # Simple test for local enhanced API
    if server_url and 'localhost' in server_url:
        try:
            response = requests.get(f"{server_url}/api/enhanced_swarm/status", timeout=10)
            if response.status_code == 200:
                print("✅ Enhanced swarm API is accessible!")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Enhanced swarm API returned: {response.status_code}")
        except Exception as e:
            print(f"❌ Could not reach enhanced swarm API: {e}")
        return
    
    print("🤖 Enhanced Universal Worker v3.0 - Enhanced Swarm Integration")
    print("Currently in TESTING mode - use 'python universal_worker_enhanced.py http://localhost:8001' to test")

if __name__ == "__main__":
    main()
