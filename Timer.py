import time
import streamlit as st

import time
import streamlit as st

def countdown(r, user, game_id):
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
        return

    mins = remaining // 60
    secs = remaining % 60

    st.subheader(f"⏱ {mins:02d}:{secs:02d}")
    st.caption(f"{remaining} seconds left")

def RenderTimer(r, user, game_id):
    settings = r.hgetall(f"game:{game_id}:settings")
    st.write(settings)
    timer_seconds = int(settings.get("timer_seconds", 0))
    st.write(timer_seconds)
    if not timer_seconds:
        return

    data = r.hgetall(f"game:{game_id}:timer")

    if not data:
        return
    # -------------------------
    # decode safely
    # -------------------------
    start = float(data.get(b"start_time", b"0").decode())
    duration = timer_seconds
    # -------------------------
    # countdown math
    # -------------------------
    elapsed = time.time() - start

    remaining = int(duration - elapsed)
    # -------------------------
    # time up
    # -------------------------
    if remaining <= 0:
        r.set(f"game:{game_id}:state", "ended")
        st.warning("⏰ Time up!")
        return
    # -------------------------
    # display
    # -------------------------
    mins = remaining // 60
    secs = remaining % 60
    st.subheader(f"⏱ {mins:02d}:{secs:02d}")
    st.caption(f"{remaining} seconds left")    


def get_timer_seconds(r, game_id):
    settings = r.hgetall(f"game:{game_id}:settings")

    value = settings.get(b"timer_seconds")
    if not value:
        return 60  # safe fallback

    return int(value.decode())