#!/usr/bin/env python3
"""
Production Server Test Script for EMTEEGEE Swarm System
Tests all swarm endpoints and worker registration on the production server.

Usage:
    python test_production_server_safe.py

This script will:
1. Test basic server connectivity
2. Test all swarm API endpoints
3. Simulate worker registration and task retrieval
4. Test heartbeat functionality
5. Verify data integrity and response formats
"""

import requests
import json
import time
import sys
from datetime import datetime
import socket
import platform

# Production server configuration
PRODUCTION_SERVER = "64.23.130.187"
BASE_URL = f"http://{PRODUCTION_SERVER}:8001"
API_BASE = f"{BASE_URL}/api/swarm"

# Test worker configuration
TEST_WORKER = {
    "worker_id": f"test_worker_{int(time.time())}",
    "worker_type": "test",
    "capabilities": ["card_analysis", "basic_processing"],
    "max_concurrent_tasks": 2,
    "status": "idle"
}

def print_header(title):
    """Print a formatted header for test sections"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_test(test_name):
    """Print test name with formatting"""
    print(f"\n[TEST] {test_name}")
    print("-" * 40)

def test_server_connectivity():
    """Test basic server connectivity"""
    print_header("SERVER CONNECTIVITY TESTS")
    
    # Test basic HTTP connectivity
    print_test("Basic HTTP Connectivity")
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"[OK] Server is reachable: HTTP {response.status_code}")
        if response.status_code == 200:
            print(f"     Response time: {response.elapsed.total_seconds():.2f}s")
        else:
            print(f"     Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Server connectivity failed: {e}")
        return False
    
    # Test TCP port connectivity
    print_test("TCP Port 8001 Connectivity")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((PRODUCTION_SERVER, 8001))
        sock.close()
        if result == 0:
            print(f"[OK] Port 8001 is open and accessible")
        else:
            print(f"[ERROR] Port 8001 is not accessible")
            return False
    except Exception as e:
        print(f"[ERROR] Port test failed: {e}")
        return False
    
    return True

def test_api_endpoints():
    """Test all swarm API endpoints"""
    print_header("SWARM API ENDPOINT TESTS")
    
    endpoints_to_test = [
        {
            "name": "Worker Registration",
            "method": "POST",
            "url": f"{API_BASE}/register",
            "data": TEST_WORKER,
            "expected_status": [200, 201]
        },
        {
            "name": "Get Work",
            "method": "GET",
            "url": f"{API_BASE}/get_work/{TEST_WORKER['worker_id']}",
            "expected_status": [200, 204]
        },
        {
            "name": "Worker Status",
            "method": "GET",
            "url": f"{API_BASE}/worker_status/{TEST_WORKER['worker_id']}",
            "expected_status": [200, 404]
        },
        {
            "name": "Heartbeat",
            "method": "POST",
            "url": f"{API_BASE}/heartbeat",
            "data": {
                "worker_id": TEST_WORKER['worker_id'],
                "status": "active",
                "current_tasks": []
            },
            "expected_status": [200]
        },
        {
            "name": "Submit Results",
            "method": "POST",
            "url": f"{API_BASE}/submit_results",
            "data": {
                "worker_id": TEST_WORKER['worker_id'],
                "task_id": "test_task_123",
                "results": {
                    "card_name": "Test Card",
                    "analysis": "Test analysis results",
                    "completed_at": datetime.now().isoformat()
                }
            },
            "expected_status": [200, 201, 404]  # 404 is OK if task doesn't exist
        },
        {
            "name": "Queue Status",
            "method": "GET",
            "url": f"{API_BASE}/queue_status",
            "expected_status": [200]
        },
        {
            "name": "Worker List",
            "method": "GET",
            "url": f"{API_BASE}/workers",
            "expected_status": [200]
        }
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        print_test(endpoint["name"])
        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"], timeout=10)
            elif endpoint["method"] == "POST":
                headers = {"Content-Type": "application/json"}
                data = endpoint.get("data", {})
                response = requests.post(endpoint["url"], 
                                       json=data, 
                                       headers=headers, 
                                       timeout=10)
            
            status_ok = response.status_code in endpoint["expected_status"]
            
            if status_ok:
                print(f"[OK] Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"     Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"     Response: {response.text[:200]}")
            else:
                print(f"[ERROR] Status: {response.status_code} (expected: {endpoint['expected_status']})")
                print(f"        Response: {response.text[:200]}")
            
            results.append({
                "endpoint": endpoint["name"],
                "status": response.status_code,
                "success": status_ok,
                "response_time": response.elapsed.total_seconds()
            })
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            results.append({
                "endpoint": endpoint["name"],
                "status": "ERROR",
                "success": False,
                "error": str(e)
            })
    
    return results

def test_worker_workflow():
    """Test complete worker workflow simulation"""
    print_header("WORKER WORKFLOW SIMULATION")
    
    worker_id = f"workflow_test_{int(time.time())}"
    
    # Step 1: Register worker
    print_test("Step 1: Worker Registration")
    try:
        register_data = {
            "worker_id": worker_id,
            "worker_type": "test_workflow",
            "capabilities": ["card_analysis"],
            "max_concurrent_tasks": 1,
            "status": "idle"
        }
        
        response = requests.post(f"{API_BASE}/register", 
                               json=register_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"[OK] Worker registered successfully: {response.status_code}")
        else:
            print(f"[ERROR] Worker registration failed: {response.status_code}")
            print(f"        Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Worker registration error: {e}")
        return False
    
    # Step 2: Send heartbeat
    print_test("Step 2: Heartbeat")
    try:
        heartbeat_data = {
            "worker_id": worker_id,
            "status": "active",
            "current_tasks": []
        }
        
        response = requests.post(f"{API_BASE}/heartbeat", 
                               json=heartbeat_data, 
                               headers={"Content-Type": "application/json"},
                               timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Heartbeat successful: {response.status_code}")
        else:
            print(f"[ERROR] Heartbeat failed: {response.status_code}")
            print(f"        Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Heartbeat error: {e}")
    
    # Step 3: Get work
    print_test("Step 3: Get Work")
    try:
        response = requests.get(f"{API_BASE}/get_work/{worker_id}", timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Work retrieved: {response.status_code}")
            work_data = response.json()
            print(f"     Work data: {json.dumps(work_data, indent=2)[:300]}...")
        elif response.status_code == 204:
            print(f"[OK] No work available (expected): {response.status_code}")
        else:
            print(f"[ERROR] Get work failed: {response.status_code}")
            print(f"        Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Get work error: {e}")
    
    # Step 4: Check worker status
    print_test("Step 4: Worker Status Check")
    try:
        response = requests.get(f"{API_BASE}/worker_status/{worker_id}", timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Worker status retrieved: {response.status_code}")
            status_data = response.json()
            print(f"     Status: {json.dumps(status_data, indent=2)}")
        else:
            print(f"[ERROR] Worker status check failed: {response.status_code}")
            print(f"        Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Worker status error: {e}")
    
    return True

def test_queue_management():
    """Test queue management endpoints"""
    print_header("QUEUE MANAGEMENT TESTS")
    
    # Test queue status
    print_test("Queue Status")
    try:
        response = requests.get(f"{API_BASE}/queue_status", timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Queue status retrieved: {response.status_code}")
            queue_data = response.json()
            print(f"     Queue info: {json.dumps(queue_data, indent=2)}")
        else:
            print(f"[ERROR] Queue status failed: {response.status_code}")
            print(f"        Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Queue status error: {e}")
    
    # Test worker list
    print_test("Active Workers List")
    try:
        response = requests.get(f"{API_BASE}/workers", timeout=10)
        
        if response.status_code == 200:
            print(f"[OK] Workers list retrieved: {response.status_code}")
            workers_data = response.json()
            print(f"     Workers: {json.dumps(workers_data, indent=2)}")
        else:
            print(f"[ERROR] Workers list failed: {response.status_code}")
            print(f"        Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Workers list error: {e}")

def generate_test_report(api_results):
    """Generate and display test report"""
    print_header("TEST REPORT SUMMARY")
    
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Production Server: {PRODUCTION_SERVER}")
    print(f"Test Platform: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")
    
    print("\nAPI Endpoint Results:")
    print("-" * 50)
    
    total_tests = len(api_results)
    successful_tests = sum(1 for result in api_results if result.get("success", False))
    
    for result in api_results:
        status_icon = "[OK]" if result.get("success", False) else "[FAIL]"
        endpoint_name = result["endpoint"].ljust(20)
        status = str(result["status"]).ljust(10)
        
        if "response_time" in result:
            time_info = f"({result['response_time']:.2f}s)"
        else:
            time_info = ""
        
        print(f"{status_icon} {endpoint_name} {status} {time_info}")
    
    print("-" * 50)
    print(f"Success Rate: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    if successful_tests == total_tests:
        print("\n[SUCCESS] All tests passed! The production server is ready for swarm operations.")
    elif successful_tests > total_tests * 0.7:
        print("\n[WARNING] Most tests passed. Some endpoints may need attention.")
    else:
        print("\n[CRITICAL] Many tests failed. Server configuration may need review.")

def main():
    """Main test execution"""
    print("EMTEEGEE Production Server Test Suite")
    print(f"Testing server: {PRODUCTION_SERVER}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Server connectivity
    if not test_server_connectivity():
        print("\n[CRITICAL] Server connectivity failed. Cannot proceed with API tests.")
        sys.exit(1)
    
    # Test 2: API endpoints
    api_results = test_api_endpoints()
    
    # Test 3: Worker workflow
    test_worker_workflow()
    
    # Test 4: Queue management
    test_queue_management()
    
    # Generate report
    generate_test_report(api_results)
    
    print(f"\nTest completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Check the output above for detailed results.")

if __name__ == "__main__":
    main()
