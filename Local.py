import redis
import streamlit as st
st.write(123)

r = redis.Redis(
    host="redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com",
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],  # your long token
    ssl=True,
    ssl_cert_reqs=None
)

print(r.ping())