import redis
import streamlit as st
st.write(1234)


r = redis.from_url(
    f"rediss://default:{st.secrets['REDIS_PASSWORD']}@redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com:11322",
    ssl_cert_reqs=None
)

print(r.ping())
print(r.ping())