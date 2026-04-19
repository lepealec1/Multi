import Functions
import streamlit as st
import time, uuid, redis
import LobbyFunctions
import admin
import Timer
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
    user, display_name = LobbyFunctions.init_user(r)
    LobbyFunctions.view_lobbies(r)

    LobbyFunctions.create_game(r, user)

    LobbyFunctions.render_lobby(r, user)

    LobbyFunctions.leave_game(r, user)

    LobbyFunctions.delete_lobby(r, user)
    game_id = st.session_state.get("game_id")

    if game_id:
        LobbyFunctions.SelectGame(r, user, game_id)  


LobbyFunctions.refresh_button()

with st.expander("Game", expanded=True):

    # -------------------------
    # STATE (RAW + CLEAN)
    # -------------------------
    raw_state = r.get(f"game:{game_id}:state")
    state = Functions.safe_decode(raw_state)


    # -------------------------
    # MODE (ONLY ONE KEY!)
    # -------------------------
    raw_mode = r.get(f"game:{game_id}:mode")
    mode = Functions.safe_decode(raw_mode) or "None"



    # HARD STOP IF NOT GAME MODE
    if mode != "Werewords":
        st.stop()

    # -------------------------
    # ROLE DEBUG
    # -------------------------


    # -------------------------
    # LOBBY
    # -------------------------
    if state in [None, "lobby"]:
        Werewords.SelectMayor(r, user, game_id)
        Werewords.StartSetup(r, user, game_id)

    # -------------------------
    # READY    mayor = r.get(f"game:{game_id}:mayor")
    # -------------------------
    elif state == "ready":
        Werewords.AssignRoles(r,user ,game_id)
        Werewords.MayorSelectWord(r,user,game_id)

    # -------------------------
    # WORD SELECTED
    # -------------------------
    elif state == "word_selected":
        Werewords.RevealRoles(r, user, game_id)
        Werewords.MayorButtons(r,user,game_id)
        Timer.Countdown()
    elif state=="discovered":
        Werewords.Discovered(r,user,game_id)
    elif state=="times_up":
        Werewords.Time(r,user,game_id)
    elif state=="no_tokens":
        Werewords.No_Tokens(r,user,game_id)

LobbyFunctions.Reset(r,user,game_id)




