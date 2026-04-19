import streamlit as st
import time, uuid, redis
import LobbyFunctions
import admin
import Werewords
def safe_decode(x):
    return x.decode() if isinstance(x, bytes) else x


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

admin.clear_db(r)

with st.expander("Multiplier Setup",expanded=True):
    user_id, display_name = LobbyFunctions.init_user(r)
    LobbyFunctions.view_lobbies(r)

    LobbyFunctions.create_game(r, user_id)

    LobbyFunctions.render_lobby(r, user_id)

    LobbyFunctions.leave_game(r, user_id)

    LobbyFunctions.delete_lobby(r, user_id)
    game_id = st.session_state.get("game_id")

    if game_id:
        LobbyFunctions.SelectGame(r, user_id, game_id)  


LobbyFunctions.refresh_button()







with st.expander("Game", expanded=True):
    role = Werewords.safe_decode(r.hget(f"game:{game_id}:roles", user_id))
    mode = Werewords.safe_decode(r.get(f"game:{game_id}:game_mode"))
    st.write(role)
    st.write(mode)
    if mode != "Werewords":
        st.stop()


    # -------------------------
    # LOBBY
    # -------------------------
    if not state or state == "lobby":
        Werewords.SelectMayor(r, user_id, game_id)
        Werewords.StartSetup(r, user_id, game_id)


    # -------------------------
    # READY
    # -------------------------
    elif state == "ready":
        Werewords.RenderRunGameButton(r, user_id, game_id)
        Werewords.RunGame(r, user_id, game_id)
    # -------------------------
    # STARTED
    # -------------------------
    elif state == "started":
        Werewords.MayorSelectWord(r, user_id, game_id)


    # -------------------------
    # WORD SELECTED
    # -------------------------
    elif state == "word_selected":
        Werewords.RevealRoles(r, user_id, game_id)


