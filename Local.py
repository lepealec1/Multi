import streamlit as st
import redis
st.write(st.secrets["REDIS_PASSWORD"])
st.write(int(st.secrets["REDIS_PORT"]))
st.write(st.secrets["REDIS_HOST"])

import redis
import streamlit as st

r = redis.from_url(
    f"rediss://default:{st.secrets['REDIS_PASSWORD']}@redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com:11322",
    decode_responses=True
)

r.ping()

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