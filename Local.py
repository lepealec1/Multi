import streamlit as st
import redis
import uuid
from streamlit_autorefresh import st_autorefresh

# -------------------------
# AUTO REFRESH (EVERY 5s)
# -------------------------
st_autorefresh(interval=5000, key="refresh")

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

if "name" not in st.session_state:
    st.session_state.name = ""

name = st.text_input("Enter your name", value=st.session_state.name)
if name:
    st.session_state.name = name

display_name = st.session_state.name if st.session_state.name else user_id

st.write(f"👤 You are: **{display_name}**")

r.hset(f"user:{user_id}", "name", display_name)

# -------------------------
# CREATE GAME
# -------------------------
st.subheader("Create Game")

create_id = st.text_input("Game ID to create")

if st.button("Create Game"):
    if create_id:
        r.set(f"game:{create_id}:exists", 1)

        # set host
        r.set(f"game:{create_id}:host", user_id)

        # add creator to lobby
        r.sadd(f"game:{create_id}:players", user_id)

        st.session_state.game_id = create_id
        st.success(f"Created game: {create_id}")
    else:
        st.error("Enter a Game ID")

# -------------------------
# JOIN GAME
# -------------------------
st.subheader("Join Game")

join_id = st.text_input("Game ID to join")

if st.button("Join Game"):
    if r.exists(f"game:{join_id}:exists"):
        r.sadd(f"game:{join_id}:players", user_id)
        st.session_state.game_id = join_id
        st.success(f"Joined {join_id}")
    else:
        st.error("Game not found")

# -------------------------
# LOBBY
# -------------------------
if "game_id" in st.session_state:
    game_id = st.session_state.game_id

    st.divider()
    st.subheader(f"🎮 Lobby: {game_id}")

    host = r.get(f"game:{game_id}:host")

    r.sadd(f"game:{game_id}:players", user_id)

    players = list(r.smembers(f"game:{game_id}:players"))

    st.write(f"👑 Host: {r.hget(f'user:{host}', 'name') if host else host}")

    st.write("### Players")

    for p in players:
        pname = r.hget(f"user:{p}", "name") or p

        col1, col2 = st.columns([3, 1])

        with col1:
            label = f"🟢 {pname} (you)" if p == user_id else f"⚪ {pname}"
            if p == host:
                label += " 👑"
            st.write(label)

        with col2:
            # allow kick ONLY if you're host and not yourself
            if user_id == host and p != user_id:
                if st.button("❌ Kick", key=f"kick_{p}"):
                    r.srem(f"game:{game_id}:players", p)
                    st.rerun()

    # -------------------------
    # LEAVE GAME
    # -------------------------
    st.divider()

    if st.button("🚪 Leave Game"):
        r.srem(f"game:{game_id}:players", user_id)

        # if host leaves, clear host
        if user_id == host:
            r.delete(f"game:{game_id}:host")

        del st.session_state.game_id
        st.rerun()