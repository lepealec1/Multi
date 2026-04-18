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

