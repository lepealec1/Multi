import streamlit as st
import redis, uuid, time


def auto_refresh(seconds=5, key="refresh"):
    if key not in st.session_state:
        st.session_state[key] = time.time()

    if time.time() - st.session_state[key] > seconds:
        st.session_state[key] = time.time()
        st.rerun()