import redis
import streamlit as st

r = redis.Redis(
    host="redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com",
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
    ssl=True,                # 🔥 REQUIRED
    ssl_cert_reqs=None       # optional (helps avoid cert issues)
)

st.warning(1)
r.ping()