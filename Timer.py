import time
import streamlit as st

def RenderTimer(r, user, game_id):

    data = r.hgetall(f"game:{game_id}:timer")

    if not data:
        return

    start = float(data.get(b"start_time", b"0").decode())
    duration = int(data.get(b"duration", b"0").decode())

    elapsed = time.time() - start
    remaining = int(duration - elapsed)

    # -------------------------
    # TIME UP
    # -------------------------
    if remaining <= 0:
        r.set(f"game:{game_id}:state", "ended")
        st.warning("⏰ Time up!")
        return

    # -------------------------
    # FORMAT TIME
    # -------------------------
    mins = remaining // 60
    secs = remaining % 60

    st.subheader(f"⏱ {mins:02d}:{secs:02d}")

    # optional debug
    st.caption(f"Time remaining: {remaining} seconds")
    
def get_timer_seconds(r, game_id):
    settings = r.hgetall(f"game:{game_id}:settings")

    value = settings.get(b"timer_seconds")
    if not value:
        return 60  # safe fallback

    return int(value.decode())