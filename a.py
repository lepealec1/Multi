"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=11322,
    decode_responses=True,
    username="default",
    password="UxXQyBngaO7mDWWesUdn7WPsDcBqRYdv",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

