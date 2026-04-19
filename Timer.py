from streamlit.runtime.scriptrunner import add_script_run_ctx
import Functions
import time
import streamlit as st

def Countdown(r, user, game_id):
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()
    settings = r.hgetall(f"game:{game_id}:settings")
    timer_seconds = int(settings.get("timer_seconds", 0))
    st.write(timer_seconds)

    duration = timer_seconds 

    elapsed = time.time() - st.session_state.start_time
    remaining = int(duration - elapsed)

    if remaining <= 0:
        st.warning("⏰ Time up!")
        r.set(f"game:{game_id}:state", "times_up")
        st.rerun()
        return

    mins = remaining // 60
    secs = remaining % 60
    raw_state = r.get(f"game:{game_id}:state")
    state = Functions.safe_decode(raw_state)
    if state == "word_selected":
        st.write(f"⏱ {mins:02d}:{secs:02d}")
        st.write(f"{remaining} seconds left")
        st.autorefresh(interval=1000, key="timer_refresh")

def Countdown(r, user, game_id):
    settings = r.hgetall(f"game:{game_id}:settings")
    timer_seconds = int(settings.get("timer_seconds", 300))

    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    placeholder = st.empty()

    while True:
        raw_state = r.get(f"game:{game_id}:state")
        state = Functions.safe_decode(raw_state)

        if state != "word_selected":
            break

        elapsed = time.time() - st.session_state.start_time
        remaining = int(timer_seconds - elapsed)

        if remaining <= 0:
            placeholder.warning("⏰ Time up!")
            r.set(f"game:{game_id}:state", "times_up")
            break

        mins = remaining // 60
        secs = remaining % 60

        placeholder.write(f"⏱ {mins:02d}:{secs:02d}")

        time.sleep(1)