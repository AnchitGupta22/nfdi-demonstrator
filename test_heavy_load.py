# test_heavy_load.py
import requests
import concurrent.futures
import time
from collections import Counter

def test_heavy_concurrent_load():
    """Test with heavier concurrent load"""
    print("🔥 Testing heavy concurrent load...")
    
    def make_info_request(i):
        start = time.time()
        try:
            resp = requests.get("http://localhost:8000/api/info", timeout=10)
            return {
                'id': i,
                'status': resp.status_code,
                'worker_pid': resp.json().get('worker_pid'),
                'response_time': time.time() - start
            }
        except Exception as e:
            return {
                'id': i,
                'status': 'error',
                'error': str(e),
                'response_time': time.time() - start
            }
    
    # Test with 50 concurrent requests
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(make_info_request, i) for i in range(50)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful = [r for r in results if r['status'] == 200]
    failed = [r for r in results if r['status'] != 200]
    worker_distribution = Counter(r['worker_pid'] for r in successful if r.get('worker_pid'))
    
    avg_response_time = sum(r['response_time'] for r in successful) / len(successful) if successful else 0
    
    print(f"📊 Heavy Load Test Results:")
    print(f"   Total requests: 50")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(failed)}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average response time: {avg_response_time:.3f}s")
    print(f"   Worker distribution: {dict(worker_distribution)}")
    print(f"   Requests per second: {len(successful)/total_time:.1f}")

if __name__ == "__main__":
    test_heavy_concurrent_load()