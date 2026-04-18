import streamlit as st
import time, admin, uuid, redis
import functions
import LobbyFunctions


# 2.2MB
if "name" not in st.session_state:
    st.session_state.name = ""



r = redis.Redis(
    host='redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
    decode_responses=True
)

if "last_version" not in st.session_state:
    st.session_state.last_version = r.get("game:version")

current = r.get("game:version")

if current != st.session_state.last_version:
    st.session_state.last_version = current
    st.rerun()


user_id, display_name = LobbyFunctions.init_user(r)

LobbyFunctions.create_game(r, user_id)

LobbyFunctions.render_lobby(r, user_id)
LobbyFunctions.leave_game(r, user_id)
LobbyFunctions.delete_lobby(r, user_id)
LobbyFunctions.view_lobbies(r)



LobbyFunctions.refresh_button
