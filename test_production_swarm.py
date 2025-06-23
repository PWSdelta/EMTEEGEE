#!/usr/bin/env python3
"""
Comprehensive test script for EMTEEGEE Production Swarm System
Tests all swarm endpoints on the production server (64.23.130.187)
"""

import requests
import json
import time
import sys
from datetime import datetime

# Production server configuration
PRODUCTION_URL = "http://64.23.130.187:8001"
WORKER_ID = f"test_worker_{int(time.time())}"

def log_test(test_name, status, details=""):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "?"
    print(f"[{timestamp}] {status_symbol} {test_name}: {status}")
    if details:
        print(f"    Details: {details}")
    print()

def test_server_connection():
    """Test basic server connectivity"""
    try:
        response = requests.get(f"{PRODUCTION_URL}/", timeout=10)
        if response.status_code == 200:
            log_test("Server Connection", "PASS", f"Status: {response.status_code}")
            return True
        else:
            log_test("Server Connection", "FAIL", f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        log_test("Server Connection", "FAIL", f"Error: {str(e)}")
        return False

def test_swarm_status():
    """Test swarm status endpoint"""
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/swarm/status/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test("Swarm Status", "PASS", f"Active workers: {data.get('active_workers', 0)}, Queue size: {data.get('queue_size', 0)}")
            return True, data
        else:
            log_test("Swarm Status", "FAIL", f"Status: {response.status_code}")
            return False, None
    except requests.exceptions.RequestException as e:
        log_test("Swarm Status", "FAIL", f"Error: {str(e)}")
        return False, None
    except json.JSONDecodeError as e:
        log_test("Swarm Status", "FAIL", f"JSON decode error: {str(e)}")
        return False, None

def test_worker_registration():
    """Test worker registration endpoint"""
    try:
        payload = {
            "worker_id": WORKER_ID,
            "capabilities": ["card_analysis", "text_processing"],
            "hardware_info": {
                "cpu_count": 8,
                "memory_gb": 16,
                "gpu_available": False
            }
        }
        
        response = requests.post(
            f"{PRODUCTION_URL}/api/swarm/register/",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            log_test("Worker Registration", "PASS", f"Worker ID: {WORKER_ID}")
            return True, data
        else:
            log_test("Worker Registration", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        log_test("Worker Registration", "FAIL", f"Error: {str(e)}")
        return False, None

def test_heartbeat():
    """Test worker heartbeat endpoint"""
    try:
        payload = {
            "worker_id": WORKER_ID,
            "status": "active",
            "current_task": None,
            "performance_metrics": {
                "tasks_completed": 0,
                "average_task_time": 0,
                "error_count": 0
            }
        }
        
        response = requests.post(
            f"{PRODUCTION_URL}/api/swarm/heartbeat/",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("Worker Heartbeat", "PASS", f"Heartbeat sent successfully")
            return True
        else:
            log_test("Worker Heartbeat", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        log_test("Worker Heartbeat", "FAIL", f"Error: {str(e)}")
        return False

def test_get_work():
    """Test get work endpoint"""
    try:
        payload = {
            "worker_id": WORKER_ID,
            "capabilities": ["card_analysis", "text_processing"],
            "max_tasks": 1
        }
        
        response = requests.post(
            f"{PRODUCTION_URL}/api/swarm/get_work/",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tasks = data.get('tasks', [])
            if tasks:
                log_test("Get Work", "PASS", f"Received {len(tasks)} task(s)")
                return True, tasks[0] if tasks else None
            else:
                log_test("Get Work", "PASS", "No tasks available (queue empty)")
                return True, None
        else:
            log_test("Get Work", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        log_test("Get Work", "FAIL", f"Error: {str(e)}")
        return False, None

def test_submit_results(task_data=None):
    """Test submit results endpoint"""
    try:
        # Create a mock result
        payload = {
            "worker_id": WORKER_ID,
            "task_id": task_data.get('task_id') if task_data else f"test_task_{int(time.time())}",
            "card_id": task_data.get('card_id') if task_data else "test_card_123",
            "results": {
                "analysis_complete": True,
                "test_mode": True,
                "timestamp": datetime.now().isoformat()
            },
            "status": "completed",
            "processing_time": 1.5
        }
        
        response = requests.post(
            f"{PRODUCTION_URL}/api/swarm/submit_results/",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            log_test("Submit Results", "PASS", f"Results submitted successfully")
            return True
        else:
            log_test("Submit Results", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        log_test("Submit Results", "FAIL", f"Error: {str(e)}")
        return False

def test_workers_list():
    """Test workers list endpoint"""
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/swarm/workers/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            workers = data.get('workers', [])
            log_test("Workers List", "PASS", f"Found {len(workers)} worker(s)")
            return True, workers
        else:
            log_test("Workers List", "FAIL", f"Status: {response.status_code}")
            return False, None
    except requests.exceptions.RequestException as e:
        log_test("Workers List", "FAIL", f"Error: {str(e)}")
        return False, None

def run_comprehensive_test():
    """Run all tests in sequence"""
    print("=" * 80)
    print("EMTEEGEE Production Swarm System Test")
    print(f"Production Server: {PRODUCTION_URL}")
    print(f"Test Worker ID: {WORKER_ID}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Test 1: Server Connection
    if not test_server_connection():
        print("❌ Server connection failed. Aborting remaining tests.")
        return False
    
    # Test 2: Swarm Status
    status_success, status_data = test_swarm_status()
    if not status_success:
        print("⚠️  Swarm status failed, but continuing with other tests...")
    
    # Test 3: Worker Registration
    reg_success, reg_data = test_worker_registration()
    if not reg_success:
        print("⚠️  Worker registration failed, but continuing with other tests...")
    
    # Test 4: Heartbeat
    test_heartbeat()
    
    # Test 5: Get Work
    work_success, task_data = test_get_work()
    
    # Test 6: Submit Results
    test_submit_results(task_data)
    
    # Test 7: Workers List
    test_workers_list()
    
    print("=" * 80)
    print("Test Summary:")
    print(f"✓ All endpoint tests completed")
    print(f"✓ Worker ID used: {WORKER_ID}")
    print(f"✓ Server: {PRODUCTION_URL}")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
