import streamlit as st
import time

def Countdown():

    duration = 300

    # -------------------------
    # LOCK START TIME ONCE
    # -------------------------
    if "start_time" not in st.session_state or st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    elapsed = time.time() - st.session_state.start_time
    remaining = int(duration - elapsed)

    # -------------------------
    # DEBUG (IMPORTANT)
    # -------------------------
    st.write("start:", st.session_state.start_time)
    st.write("elapsed:", elapsed)
    st.write("remaining:", remaining)

    # -------------------------
    # TIME UP
    # -------------------------
    if remaining <= 0:
        st.warning("⏰ Time up!")
        return

    # -------------------------
    # DISPLAY
    # -------------------------
    st.subheader(f"{remaining//60:02d}:{remaining%60:02d}")

    # -------------------------
    # AUTO REFRESH
    # -------------------------
    st.autorefresh(interval=1000, key="timer_refresh")