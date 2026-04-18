import redis, ssl

r = redis.from_url(
    "rediss://default:YOUR_PASSWORD@redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com:11322",
    ssl_cert_reqs=ssl.CERT_NONE
)

print(r.ping())