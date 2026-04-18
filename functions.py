import streamlit as st
import redis, uuid, time

def auto_refresh(seconds=5):
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()

    if time.time() - st.session_state.last_refresh > seconds:
        st.session_state.last_refresh = time.time()
        st.rerun()