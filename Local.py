import streamlit as st
import redis

r = redis.Redis(
    host=st.secrets["REDIS_HOST"],
    port=int(st.secrets["REDIS_PORT"]),
    username=st.secrets["REDIS_USERNAME"],
    password=st.secrets["REDIS_PASSWORD"],
    ssl=True,
    ssl_cert_reqs=None,
    decode_responses=True
)

r.ping()