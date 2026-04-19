import time
import streamlit as st

def RenderTimer(r, user, game_id):
    data = r.hgetall(f"game:{game_id}:timer")
    if not data:
        return
    start = float(data[b"start_time"].decode())
    duration = int(data[b"duration"].decode())

    remaining = int(duration - (time.time() - start))

    if remaining <= 0:
        r.set(f"game:{game_id}:state", "ended")
        st.warning("⏰ Time up!")
        return

    st.subheader(f"⏱ {remaining//60:02d}:{remaining%60:02d}")
    
def get_timer_seconds(r, game_id):
    settings = r.hgetall(f"game:{game_id}:settings")

    value = settings.get(b"timer_seconds")
    if not value:
        return 60  # safe fallback

    return int(value.decode())