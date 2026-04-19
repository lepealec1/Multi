import streamlit as st
import time

def Countdown(duration=300, key="timer"):

    if key not in st.session_state:
        st.session_state[key] = time.time()

    elapsed = time.time() - st.session_state[key]
    remaining = int(duration - elapsed)

    if remaining <= 0:
        st.warning("⏰ Time up!")
        return

    st.subheader(f"{remaining//60:02d}:{remaining%60:02d}")

    time.sleep(1)
    st.rerun()