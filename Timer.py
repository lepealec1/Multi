import streamlit as st
import time
import Functions

def Countdown(r, user, game_id):

    timer_key = f"game:{game_id}:timer"

    data = r.hgetall(timer_key)

    if not data:
        st.warning("Timer not initialized")
        return

    # -------------------------
    # SAFE decode
    # -------------------------
    start = float(data.get(b"start_time", b"0").decode())
    duration = int(data.get(b"duration", b"0").decode())

    # -------------------------
    # COUNTDOWN LOGIC
    # -------------------------
    elapsed = time.time() - start
    remaining = int(duration - elapsed)

    st.write("elapsed:", elapsed)
    st.write("remaining:", remaining)
    st.write("duration:", duration)

    # -------------------------
    # TIME UP
    # -------------------------
    if remaining <= 0:
        st.warning("⏰ Time up!")
        r.set(f"game:{game_id}:state", "times_up")
        return

    # -------------------------
    # DISPLAY ONLY WHEN ACTIVE
    # -------------------------
    raw_state = r.get(f"game:{game_id}:state")
    state = Functions.safe_decode(raw_state)

    if state == "word_selected":
        mins = remaining // 60
        secs = remaining % 60

        st.subheader(f"⏱ {mins:02d}:{secs:02d}")
        st.caption(f"{remaining} seconds left")

        st.autorefresh(interval=1000, key=f"{game_id}_timer")