import streamlit as st
import redis
import uuid

# -------------------------
# REDIS CONNECTION
# -------------------------
r = redis.Redis(
    host='redis-11322.c12.us-east-1-4.ec2.cloud.redislabs.com',
    port=11322,
    username="default",
    password=st.secrets["REDIS_PASSWORD"],
    decode_responses=True
)

st.title("🎮 Multiplayer Lobby")

# -------------------------
# USER ID (persistent per session)
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

user_id = st.session_state.user_id

st.write(f"Your ID: `{user_id}`")

# -------------------------
# CREATE GAME
# -------------------------
st.subheader("Create Game")

if st.button("Create New Game"):
    game_id = str(uuid.uuid4())[:6]

    # create game player set
    r.sadd(f"game:{game_id}:players", user_id)

    # store game exists flag
    r.set(f"game:{game_id}:exists", 1)

    st.session_state.game_id = game_id
    st.success(f"Game created! ID: {game_id}")
    st.rerun()

# -------------------------
# JOIN GAME
# -------------------------
st.subheader("Join Game")

join_id = st.text_input("Enter Game ID")

if st.button("Join Game"):
    if r.exists(f"game:{join_id}:exists"):
        r.sadd(f"game:{join_id}:players", user_id)
        st.session_state.game_id = join_id
        st.success(f"Joined game {join_id}")
        st.rerun()
    else:
        st.error("Game not found")

# -------------------------
# IN GAME VIEW
# -------------------------
if "game_id" in st.session_state:
    game_id = st.session_state.game_id

    st.divider()
    st.subheader(f"Game: {game_id}")

    # add yourself (safe if already added)
    r.sadd(f"game:{game_id}:players", user_id)

    # get players
    players = r.smembers(f"game:{game_id}:players")

    st.write("### Players in lobby:")
    for p in players:
        if p == user_id:
            st.write(f"🟢 {p} (you)")
        else:
            st.write(f"⚪ {p}")

    # -------------------------
    # LEAVE GAME
    # -------------------------
    if st.button("Leave Game"):
        r.srem(f"game:{game_id}:players", user_id)
        del st.session_state.game_id
        st.rerun()

    # -------------------------
    # AUTO REFRESH
    # -------------------------
    st.caption("Auto-refreshing...")
    st.experimental_rerun()