import streamlit as st
import time, uuid, redis
import LobbyFunctions
import admin
import Werewords


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

  
with st.expander("Game",expanded=True):
    state = r.get(f"game:{game_id}:state")
    st.write(state);
    state = state.decode() if isinstance(state, bytes) else state
    st.write(state);

    if st.session_state.get("game_mode") == "Werewords":
        state = r.get(f"game:{game_id}:state")
        state = state.decode() if isinstance(state, bytes) else state
        #Werewords.RenderTimer(r, user_id, game_id)
        if state in [None, "lobby"]:
            Werewords.SelectMayor(r, user_id, game_id)
            Werewords.StartSetup(r, user_id, game_id)
            st.rerun()
        # -------------------------
        # READY PHASE
        # -------------------------
        elif state == "ready":
            Werewords.RenderRunGameButton(r, user_id, game_id)
            Werewords.RunGame(r, user_id, game_id)
            st.rerun()
        # -------------------------
        # GAME STARTED PHASE
        # -------------------------
        elif state == "started":
            Werewords.MayorSelectWord(r, user_id, game_id)
        # -------------------------
        # WORD LOCKED PHASE
        # -------------------------
        elif state == "word_selected":
            Werewords.RevealRoles(r, user_id, game_id)
            st.rerun()


role = Werewords.safe_decode(r.hget(f"game:{game_id}:roles", user_id))
st.write(role)


LobbyFunctions.refresh_button()

state = r.get(f"game:{game_id}:state")
st.write("Game State:");
st.write(state);

state = r.get(f"game:{game_id}:role")
st.write("role:");
st.write(role);
