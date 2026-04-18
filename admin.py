import streamlit as st
import redis, uuid, time


#ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")
def clear_db(r):
    display_name = st.session_state.name
    if display_name == "alepe":

        st.subheader("🧹 Admin Tools")
        ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "a")

        password = st.text_input("Enter admin password", type="password")

        if st.button("🚨 DELETE ALL REDIS DATA"):
            if password == ADMIN_PASSWORD:
                r.flushdb()
                st.success("🔥 All Redis data cleared!")
                st.rerun()
            else:
                st.error("❌ Wrong password")

import streamlit as st

def admin_clear_lobby(r, user_id):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    display_name = st.session_state.get("name", "")
    host_id = r.get(f"game:{game_id}:host")

    # ONLY admin ("alepe")
    is_admin = (display_name == "alepe")

    if not is_admin:
        return

    st.divider()
    st.subheader("🧹 Admin Controls")

    if st.button("🚨 Clear This Lobby (Kick Everyone)"):

        # remove all lobby data (ONLY this game)
        r.delete(f"game:{game_id}:exists")
        r.delete(f"game:{game_id}:host")
        r.delete(f"game:{game_id}:players")

        # remove session state
        del st.session_state.game_id

        st.success("Lobby cleared by admin")
        st.rerun()