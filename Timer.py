import streamlit as st
import time

def Countdown(reset=False):

    duration = 300

    if reset or "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    elapsed = time.time() - st.session_state.start_time
    remaining = int(duration - elapsed)

    st.write("start:", st.session_state.start_time)
    st.write("elapsed:", elapsed)
    st.write("remaining:", remaining)

    if remaining <= 0:
        st.warning("⏰ Time up!")
        return

    st.subheader(f"{remaining//60:02d}:{remaining%60:02d}")

    st.autorefresh(interval=1000, key="timer_refresh")