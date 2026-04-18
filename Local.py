import streamlit as st
import redis
st.write(st.secrets["REDIS_PASSWORD"])
st.write(int(st.secrets["REDIS_PORT"]))
st.write(st.secrets["REDIS_HOST"])



r = redis.Redis(
    host="redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com",
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
    ssl=True,
    ssl_cert_reqs=None,
    decode_responses=True
)

print(r.ping())