import streamlit as st
import time, admin, uuid, redis
import functions
import LobbyFunctions


# 2.2MB
if "name" not in st.session_state:
    st.session_state.name = ""


import time
import streamlit as st

# only refresh occasionally


r = redis.Redis(
    host='redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
    decode_responses=True
)

now = time.time()

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = now

# always compute first
elapsed = now - st.session_state.last_refresh

if elapsed > 5:
    st.session_state.last_refresh = now
    st.rerun()
admin.clear_db(r)

user_id, display_name = LobbyFunctions.init_user(r)

LobbyFunctions.create_game(r, user_id)

LobbyFunctions.render_lobby(r, user_id)
LobbyFunctions.leave_game(r, user_id)
LobbyFunctions.delete_lobby(r, user_id)
LobbyFunctions.view_lobbies(r)



