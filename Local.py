import streamlit as st
import redis

r = redis.from_url(st.secrets["REDIS_URL"], decode_responses=True)

r.ping()
st.success("Redis connected ✅")