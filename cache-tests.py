# definitive_cache_test.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeboda.settings')
django.setup()

from django.core.cache import cache
import redis
import json

print("=" * 60)
print("DEFINITIVE CACHE TEST")
print("=" * 60)

# Test 1: Direct cache test
print("\n1. Testing Django cache directly...")
cache.set('direct_test', {'hello': 'world'}, 30)
result = cache.get('direct_test')
print(f"   Set and retrieved: {result}")

# Test 2: Check Redis directly
print("\n2. Checking Redis database 1 directly...")
try:
    r = redis.Redis(host='localhost', port=6379, db=1)
    keys = r.keys('*')
    print(f"   Found {len(keys)} keys in Redis db 1:")
    for key in keys:
        key_str = key.decode('utf-8')
        print(f"   - {key_str}")
        if b'safeboda' in key:
            value = r.get(key)
            try:
                decoded = value.decode('utf-8')
                print(f"     Value: {decoded[:100]}...")
            except:
                print(f"     Value (binary): {value[:50]}...")
except Exception as e:
    print(f"   Error connecting to Redis: {e}")

# Test 3: Check Redis database 0 (default)
print("\n3. Checking Redis database 0 (default)...")
try:
    r0 = redis.Redis(host='localhost', port=6379, db=0)
    keys0 = r0.keys('*')
    print(f"   Found {len(keys0)} keys in Redis db 0:")
    for key in keys0:
        print(f"   - {key.decode('utf-8')}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Test the actual cache key from views
print("\n4. Testing view cache key...")
from users.views import get_cache_key
cache_key = get_cache_key('user_list_response')
print(f"   View cache key: '{cache_key}'")
cached_data = cache.get(cache_key)
if cached_data:
    print(f"   ✅ Found cached user list with {len(cached_data)} users")
else:
    print(f"   ❌ No cached user list found")

# Test 5: Force cache the user list
print("\n5. Manually caching user list...")
from users.models import User
from users.serializers import UserSerializer

users = User.objects.all()
serializer = UserSerializer(users, many=True)
cache.set(cache_key, serializer.data, 300)
print(f"   Manually set cache for '{cache_key}'")

# Verify it's there
cached_again = cache.get(cache_key)
print(f"   Verified cache: {'✅ Found' if cached_again else '❌ Not found'}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)