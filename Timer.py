import streamlit as st
import time

def Countdown(duration=300, key="timer"):

    # -------------------------
    # lock start time once
    # -------------------------
    if key not in st.session_state:
        st.session_state[key] = time.time()

    # -------------------------
    # calculate time
    # -------------------------
    elapsed = time.time() - st.session_state[key]
    remaining = int(duration - elapsed)

    # -------------------------
    # placeholder (prevents flicker)
    # -------------------------
    timer_slot = st.empty()

    if remaining <= 0:
        timer_slot.warning("⏰ Time up!")
        return

    mins = remaining // 60
    secs = remaining % 60

    # -------------------------
    # ONLY this part updates
    # -------------------------
    timer_slot.markdown(f"""
        <h1 style='text-align:center;'>
        ⏱ {mins:02d}:{secs:02d}
        </h1>
    """, unsafe_allow_html=True)

    # -------------------------
    # smooth refresh
    # -------------------------
    time.sleep(1)
    st.rerun()