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
if "last_tick" not in st.session_state:
    st.session_state.last_tick = time.time()

if time.time() - st.session_state.last_tick > 5:
    st.session_state.last_tick = time.time()

    # BUT only rerun if something changed
    players = r.scard(f"game:{game_id}:players")

    if "prev_players" not in st.session_state:
        st.session_state.prev_players = players

    if players != st.session_state.prev_players:
        st.session_state.prev_players = players
        st.rerun()

r = redis.Redis(
    host='redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
    decode_responses=True
)

admin.clear_db(r)

user_id, display_name = LobbyFunctions.init_user(r)

LobbyFunctions.create_game(r, user_id)

LobbyFunctions.render_lobby(r, user_id)
LobbyFunctions.leave_game(r, user_id)
LobbyFunctions.delete_lobby(r, user_id)
LobbyFunctions.view_lobbies(r)



