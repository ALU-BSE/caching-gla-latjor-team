# final_proof.py
import requests
import time

print("PROVING CACHE IS WORKING")
print("=" * 50)

url = "http://localhost:8000/api/users/"

print("1. Making first request (should be slower)...")
start = time.time()
response1 = requests.get(url)
time1 = time.time() - start
print(f"   Time: {time1:.3f} seconds")
print(f"   Status: {response1.status_code}")

print("\n2. Making second request (should be FASTER - from cache)...")
start = time.time()
response2 = requests.get(url)
time2 = time.time() - start
print(f"   Time: {time2:.3f} seconds")
print(f"   Status: {response2.status_code}")

print("\n3. Results:")
print(f"   First request:  {time1:.3f}s")
print(f"   Second request: {time2:.3f}s")

if time2 < time1:
    speedup = time1 / time2
    print(f"   ✅ CACHING WORKS! {speedup:.1f}x faster")
else:
    print(f"   ⚠️  No speed improvement")

print("\n4. Checking Redis database 1...")
import redis
r = redis.Redis(host='localhost', port=6379, db=1)
keys = r.keys('*')
print(f"   Found {len(keys)} cached items:")
for key in keys:
    print(f"   - {key.decode('utf-8')}")