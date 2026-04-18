import streamlit as st
import redis

r = redis.Redis(
    host=st.secrets["REDIS_HOST"],
    port=int(st.secrets["REDIS_PORT"]),
    password=st.secrets["REDIS_PASSWORD"],
    ssl=True,
    decode_responses=True
)

r.ping()
st.success("Connected to Redis ✅")