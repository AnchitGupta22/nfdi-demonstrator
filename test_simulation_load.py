# test_simulation_load.py
import requests
import concurrent.futures
import time
import json
from collections import Counter

def solve_captcha_and_get_token():
    """Get a CAPTCHA token for testing"""
    # For production testing, we'll need to handle CAPTCHA properly
    # This is a simplified version - in real production you'd solve the CAPTCHA
    try:
        # Get a CAPTCHA
        captcha_resp = requests.get("http://localhost:8000/api/captcha", timeout=5)
        if captcha_resp.status_code == 200:
            captcha_data = captcha_resp.json()
            # For testing, we can't auto-solve CAPTCHA, so we'll test without it
            return None
        return None
    except:
        return None

def test_simulation_request(request_id):
    """Test a single simulation request"""
    try:
        start_time = time.time()
        
        # Simulation parameters
        sim_data = {
            "ms_id": request_id % 10,  # Cycle through first 10 microstructures
            "kappa1": 2.0 + (request_id % 5),  # Vary between 2-6
            "alpha": 30.0 + (request_id % 6) * 10  # Vary between 30-80 degrees
        }
        
        # Make the request (will fail due to CAPTCHA, but tests the endpoint)
        response = requests.post(
            "http://localhost:8000/api/simulate",
            json=sim_data,
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Check worker info to see distribution
        info_resp = requests.get("http://localhost:8000/api/info", timeout=5)
        worker_pid = info_resp.json().get('worker_pid') if info_resp.status_code == 200 else None
        
        return {
            'request_id': request_id,
            'status_code': response.status_code,
            'response_time': response_time,
            'worker_pid': worker_pid,
            'success': response.status_code == 200,
            'captcha_protected': response.status_code == 403  # Expected due to CAPTCHA
        }
        
    except Exception as e:
        return {
            'request_id': request_id,
            'error': str(e),
            'response_time': time.time() - start_time if 'start_time' in locals() else None,
            'success': False
        }

def test_concurrent_simulations(num_requests=10, max_workers=5):
    """Test concurrent simulation requests"""
    print(f"🧪 Testing {num_requests} concurrent simulation requests (CAPTCHA protected)...")
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(test_simulation_request, i) for i in range(num_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful_results = [r for r in results if r.get('success', False)]
    captcha_blocked = [r for r in results if r.get('captcha_protected', False)]
    failed_results = [r for r in results if not r.get('success', False) and not r.get('captcha_protected', False)]
    
    # Worker distribution
    worker_pids = [r['worker_pid'] for r in results if r.get('worker_pid')]
    worker_distribution = Counter(worker_pids)
    
    # Response times
    response_times = [r['response_time'] for r in results if r.get('response_time')]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    print(f"📊 Simulation Load Test Results:")
    print(f"   Total requests: {num_requests}")
    print(f"   Successful simulations: {len(successful_results)}")
    print(f"   CAPTCHA protected (expected): {len(captcha_blocked)}")
    print(f"   Failed requests: {len(failed_results)}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average response time: {avg_response_time:.3f}s")
    print(f"   Worker distribution: {dict(worker_distribution)}")
    print(f"   Requests per second: {len(results)/total_time:.1f}")
    
    # Performance assessment
    if len(captcha_blocked) == num_requests:
        print("✅ CAPTCHA protection working perfectly!")
    if len(set(worker_pids)) > 1:
        print("✅ Multi-worker load balancing working!")
    
    return results

def test_info_endpoint_under_load():
    """Test the info endpoint under heavy load"""
    print("\n🔥 Testing info endpoint under extreme load...")
    
    start_time = time.time()
    num_requests = 100
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(lambda i: requests.get("http://localhost:8000/api/info", timeout=10), i) 
            for i in range(num_requests)
        ]
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                resp = future.result()
                results.append({
                    'status': resp.status_code,
                    'worker_pid': resp.json().get('worker_pid') if resp.status_code == 200 else None
                })
            except Exception as e:
                results.append({'status': 'error', 'error': str(e)})
    
    total_time = time.time() - start_time
    
    successful = [r for r in results if r['status'] == 200]
    worker_pids = [r['worker_pid'] for r in successful if r.get('worker_pid')]
    worker_distribution = Counter(worker_pids)
    
    print(f"📊 Extreme Load Test Results:")
    print(f"   Total requests: {num_requests}")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {num_requests - len(successful)}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Requests per second: {len(successful)/total_time:.1f}")
    print(f"   Worker distribution: {dict(worker_distribution)}")

if __name__ == "__main__":
    print("🎯 Advanced Multi-Worker Performance Testing")
    print("=" * 50)
    
    # Test 1: Simulation endpoint (CAPTCHA protected)
    test_concurrent_simulations(10, 5)
    
    # Test 2: Extreme load on info endpoint
    test_info_endpoint_under_load()