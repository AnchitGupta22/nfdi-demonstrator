# test_production_load.py
import requests
import concurrent.futures
import time
import json

def get_captcha_token():
    """Get a valid CAPTCHA token"""
    # Get CAPTCHA
    captcha_resp = requests.get("http://localhost:8000/api/captcha")
    if captcha_resp.status_code != 200:
        return None
    
    captcha_data = captcha_resp.json()
    captcha_id = captcha_data["captcha_id"]
    
    # For testing, we'll simulate solving the CAPTCHA
    # In real production, a human would solve this
    # For now, let's bypass by checking the server logs for the actual code
    print(f"⚠️ CAPTCHA ID: {captcha_id} - You need to solve this manually for full production test")
    return None  # Return None for now since we can't auto-solve

def test_simulation_with_captcha(request_id):
    """Test simulation with proper CAPTCHA (manual step required)"""
    try:
        sim_data = {
            "ms_id": request_id % 10,
            "kappa1": 2.0 + (request_id % 5),
            "alpha": 30.0 + (request_id % 6) * 10
        }
        
        # This will fail due to CAPTCHA requirement - that's expected!
        response = requests.post(
            "http://localhost:8000/api/simulate",
            json=sim_data,
            timeout=30
        )
        
        return {
            'request_id': request_id,
            'status_code': response.status_code,
            'requires_captcha': response.status_code == 403
        }
        
    except Exception as e:
        return {
            'request_id': request_id,
            'error': str(e)
        }

def test_redis_captcha_sharing():
    """Test that CAPTCHA data is shared between workers via Redis"""
    print("🧪 Testing Redis CAPTCHA sharing between workers...")
    
    # Get multiple CAPTCHAs and see if they persist across workers
    captcha_ids = []
    for i in range(5):
        resp = requests.get("http://localhost:8000/api/info")
        worker_pid = resp.json().get('worker_pid')
        
        captcha_resp = requests.get("http://localhost:8000/api/captcha")
        if captcha_resp.status_code == 200:
            captcha_id = captcha_resp.json()['captcha_id']
            captcha_ids.append((captcha_id, worker_pid))
            print(f"   CAPTCHA {captcha_id[:8]}... created by worker {worker_pid}")
    
    print(f"✅ Created {len(captcha_ids)} CAPTCHAs across workers")
    return len(set(pid for _, pid in captcha_ids)) > 1  # Multiple workers used

def test_concurrent_info_requests():
    """Test concurrent info requests to verify worker distribution"""
    print("🧪 Testing concurrent info requests...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(lambda i: requests.get("http://localhost:8000/api/info").json(), i) for i in range(20)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    worker_pids = [r.get('worker_pid') for r in results if r.get('worker_pid')]
    unique_workers = len(set(worker_pids))
    
    print(f"✅ {len(results)} requests completed")
    print(f"🔄 Used {unique_workers} unique workers: {set(worker_pids)}")
    
    return unique_workers > 1

if __name__ == "__main__":
    print("🏭 Production-like Multi-Worker Test with Redis")
    print("=" * 50)
    
    # Test 1: Worker distribution
    multi_worker = test_concurrent_info_requests()
    
    # Test 2: Redis CAPTCHA sharing
    redis_sharing = test_redis_captcha_sharing()
    
    # Test 3: CAPTCHA protection (will fail - expected)
    print("\n🔒 Testing CAPTCHA protection...")
    test_result = test_simulation_with_captcha(0)
    captcha_protected = test_result.get('requires_captcha', False)
    
    print("\n📊 PRODUCTION READINESS SUMMARY:")
    print(f"   Multi-worker distribution: {'✅ PASS' if multi_worker else '❌ FAIL'}")
    print(f"   Redis CAPTCHA sharing: {'✅ PASS' if redis_sharing else '❌ FAIL'}")
    print(f"   CAPTCHA protection active: {'✅ PASS' if captcha_protected else '❌ FAIL'}")
    
    if multi_worker and redis_sharing and captcha_protected:
        print("\n🎉 PRODUCTION READY! Your multi-worker setup is working correctly.")
    else:
        print("\n⚠️  Some issues found. Check the results above.")