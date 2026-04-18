import streamlit as st
import redis
st.write(st.secrets["REDIS_PASSWORD"])
st.write(int(st.secrets["REDIS_PORT"]))
st.write(st.secrets["REDIS_HOST"])


#r.ping()
st.success("Redis connected ✅")