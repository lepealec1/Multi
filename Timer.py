import Functions
import streamlit as st
import time

def Countdown(r, user, game_id):
    #settings = r.hgetall(f"game:{game_id}:settings")
    #timer_seconds = int(settings.get("timer_seconds", 300))
    timer_seconds=300
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    raw_state = r.get(f"game:{game_id}:state")
    state = Functions.safe_decode(raw_state)

    if state != "word_selected":
        return

    elapsed = time.time() - st.session_state.start_time
    remaining = int(timer_seconds - elapsed)

    placeholder = st.empty()

    if remaining <= 0:
        placeholder.warning("⏰ Time up!")
        r.set(f"game:{game_id}:state", "times_up")
        return

    mins = remaining // 60
    secs = remaining % 60

    placeholder.write(f"⏱ {mins:02d}:{secs:02d}")
    st.write(f"⏱ {mins:02d}:{secs:02d}")
    st.warning(f"⏱ {mins:02d}:{secs:02d}")

    time.sleep(30)
    st.rerun()