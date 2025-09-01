# test_force_load_balance.py
import requests
import concurrent.futures
import time
from collections import Counter

def overwhelm_single_worker():
    """Send many concurrent requests to force load balancing"""
    print("🔥 Overwhelming single worker to force load balancing...")
    
    def make_request(i):
        try:
            start = time.time()
            resp = requests.get("http://localhost:8000/api/info", timeout=10)
            end = time.time()
            
            if resp.status_code == 200:
                return {
                    'id': i,
                    'worker_pid': resp.json().get('worker_pid'),
                    'response_time': end - start,
                    'status': 'success'
                }
            else:
                return {'id': i, 'status': f'error_{resp.status_code}'}
        except Exception as e:
            return {'id': i, 'status': f'timeout'}
    
    # Send 30 requests simultaneously to overwhelm worker 970
    print("Sending 30 concurrent requests...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(make_request, i) for i in range(30)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = [r for r in results if r.get('status') == 'success']
    worker_pids = [r['worker_pid'] for r in successful if r.get('worker_pid')]
    worker_distribution = Counter(worker_pids)
    
    print(f"\n📊 Load Balancing Test Results:")
    print(f"   Total requests: 30")
    print(f"   Successful: {len(successful)}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Unique workers used: {len(set(worker_pids))}")
    print(f"   Worker PIDs found: {sorted(set(worker_pids))}")
    print(f"   Worker distribution: {dict(worker_distribution)}")
    
    if len(set(worker_pids)) > 1:
        print("✅ SUCCESS: Multiple workers handling requests!")
        print(f"   Worker 970: {worker_distribution.get(970, 0)} requests")
        print(f"   Worker 971: {worker_distribution.get(971, 0)} requests")
        return True
    else:
        print("⚠️  Still only one worker responding")
        return False

def sustained_load_test():
    """Sustained load over time to force worker switching"""
    print("\n🔄 Sustained load test...")
    
    worker_pids = set()
    request_count = 0
    
    # Send requests for 10 seconds
    end_time = time.time() + 10
    
    while time.time() < end_time:
        try:
            resp = requests.get("http://localhost:8000/api/info", timeout=2)
            if resp.status_code == 200:
                pid = resp.json().get('worker_pid')
                worker_pids.add(pid)
                request_count += 1
                
                if len(worker_pids) > 1:
                    print(f"✅ Multiple workers detected: {worker_pids}")
                    break
                    
        except:
            pass
        
        time.sleep(0.1)
    
    print(f"📊 Sustained test: {request_count} requests, {len(worker_pids)} workers")
    return len(worker_pids) > 1

if __name__ == "__main__":
    print("🎯 Force Load Balancing Test")
    print("=" * 40)
    
    # Test 1: Overwhelm with concurrent requests
    concurrent_success = overwhelm_single_worker()
    
    # Test 2: Sustained load
    sustained_success = sustained_load_test()
    
    print(f"\n🎯 SUMMARY:")
    if concurrent_success or sustained_success:
        print("✅ Load balancing working - both workers can handle requests")
    else:
        print("🔧 Need to restart Gunicorn with --preload-app flag")