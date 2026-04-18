import streamlit as st
import time, admin, uuid, redis
import functions
import lobby_functions


# 2.2MB
if "name" not in st.session_state:
    st.session_state.name = ""
functions.auto_refresh(5)

r = redis.Redis(
    host='redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
    decode_responses=True
)

admin.clear_db(r)

user_id, display_name = lobby_functions.init_user(r)

lobby_functions.create_game(r, user_id)
lobby_functions.join_game(r, user_id)

lobby_functions.render_lobby(r, user_id)
lobby_functions.leave_game(r, user_id)
lobby_functions.delete_lobby(r, user_id)
lobby_functions.view_lobbies(r)


