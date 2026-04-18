import streamlit as st
import redis, uuid, time

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "a")
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

def admin_clear_lobby(r):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    display_name = st.session_state.get("name", "")

    is_admin = (display_name == "alepe")

    if not is_admin:
        return

    st.subheader("🧹 Admin Lobby Control")

    confirm = st.checkbox("Confirm: delete this lobby")

    if st.button("🚨 Clear This Lobby"):
        if confirm:
            # delete ONLY this lobby
            r.delete(f"game:{game_id}:exists")
            r.delete(f"game:{game_id}:host")
            r.delete(f"game:{game_id}:players")

            # cleanup session
            del st.session_state.game_id

            st.success(f"Lobby '{game_id}' cleared")
            st.rerun()
        else:
            st.warning("Check confirmation box first")