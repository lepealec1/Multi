from streamlit.runtime.scriptrunner import add_script_run_ctx
import streamlit as st
import time

def Countdown(duration=300, key="timer"):

    # -------------------------
    # set start time once
    # -------------------------
    if key not in st.session_state:
        st.session_state[key] = time.time()

    # -------------------------
    # compute remaining time
    # -------------------------
    elapsed = time.time() - st.session_state[key]
    remaining = int(duration - elapsed)

    # -------------------------
    # time up
    # -------------------------
    if remaining <= 0:
        st.warning("⏰ Time up!")
        return 0

    # -------------------------
    # display
    # -------------------------
    mins = remaining // 60
    secs = remaining % 60

    st.subheader(f"⏱ {mins:02d}:{secs:02d}")
    st.caption(f"{remaining} seconds left")

    # -------------------------
    # auto refresh
    # -------------------------
    st.autorefresh(interval=1000, key=f"{key}_refresh")

    return remaining