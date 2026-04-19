import streamlit as st
import time

def Countdown():

    duration = 300  # 5 minutes

    # -------------------------
    # lock start time once
    # -------------------------
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    # -------------------------
    # math
    # -------------------------
    elapsed = time.time() - st.session_state.start_time
    remaining = int(duration - elapsed)

    # -------------------------
    # time up
    # -------------------------
    if remaining <= 0:
        st.warning("⏰ Time up!")
        return

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
    st.autorefresh(interval=1000, key="timer_refresh")