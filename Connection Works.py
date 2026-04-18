import redis
import streamlit as st
st.write(1)


r = redis.Redis(
    host='redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=11322,
    decode_responses=True,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
)
success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
st.write(result)
# >>> bar

