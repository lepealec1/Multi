import redis
import streamlit as st

r = redis.from_url(
    f"rediss://default:{st.secrets['REDIS_PASSWORD']}@redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com:11322",
    decode_responses=True
)

r.ping()