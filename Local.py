import streamlit as st
import redis

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
# USER SETUP
# -------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

user_id = st.session_state.user_id

# 👇 NEW: user name input
if "name" not in st.session_state:
    st.session_state.name = ""

st.subheader("👤 Your Info")
name = st.text_input("Enter your name", value=st.session_state.name)

if name:
    st.session_state.name = name

display_name = st.session_state.name if st.session_state.name else user_id

st.write(f"Hello: **{display_name}**")

# store user name in redis
r.hset(f"user:{user_id}", "name", display_name)

# -------------------------
# CREATE GAME (custom ID)
# -------------------------
st.subheader("Create Game")

custom_game_id = st.text_input("Enter Game ID to create (e.g. lobby1)")

if st.button("Create Game"):
    if not custom_game_id:
        st.error("Please enter a Game ID")
    else:
        r.set(f"game:{custom_game_id}:exists", 1)
        r.sadd(f"game:{custom_game_id}:players", user_id)

        st.session_state.game_id = custom_game_id
        st.success(f"Game created: {custom_game_id}")
        st.rerun()

# -------------------------
# JOIN GAME
# -------------------------
st.subheader("Join Game")

join_id = st.text_input("Enter Game ID to join")

if st.button("Join Game"):
    if r.exists(f"game:{join_id}:exists"):
        r.sadd(f"game:{join_id}:players", user_id)
        st.session_state.game_id = join_id
        st.success(f"Joined game {join_id}")
        st.rerun()
    else:
        st.error("Game not found")

# -------------------------
# LOBBY
# -------------------------
if "game_id" in st.session_state:
    game_id = st.session_state.game_id

    st.divider()
    st.subheader(f"🎮 Lobby: {game_id}")

    r.sadd(f"game:{game_id}:players", user_id)

    players = r.smembers(f"game:{game_id}:players")

    st.write("### Players")

    for p in players:
        pname = r.hget(f"user:{p}", "name") or p

        if p == user_id:
            st.write(f"🟢 {pname} (you)")
        else:
            st.write(f"⚪ {pname}")

    # -------------------------
    # LEAVE GAME
    # -------------------------
    if st.button("Leave Game"):
        r.srem(f"game:{game_id}:players", user_id)
        del st.session_state.game_id
        st.rerun()

    st.caption("Refresh page to update players")