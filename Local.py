import streamlit as st
import redis
import uuid
import time, admin
# -------------------------
# AUTO REFRESH (every 5s)
# -------------------------
if "name" not in st.session_state:
    st.session_state.name = ""
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = time.time()
    st.rerun()


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

admin.clear_db(r)



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

# store name in redis
r.hset(f"user:{user_id}", "name", display_name)

# -------------------------
# CREATE GAME
# -------------------------
st.subheader("Create Game")

create_id = st.text_input("Game ID to create")

if st.button("Create Game"):
    if create_id:
        r.set(f"game:{create_id}:exists", 1)

        # host = user_id (IMPORTANT)
        r.set(f"game:{create_id}:host", user_id)

        r.sadd(f"game:{create_id}:players", user_id)

        st.session_state.game_id = create_id
        st.success(f"Created game: {create_id}")
        st.rerun()
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

    host_id = r.get(f"game:{game_id}:host")

    r.sadd(f"game:{game_id}:players", user_id)

    players = list(r.smembers(f"game:{game_id}:players"))

    host_name = r.hget(f"user:{host_id}", "name") if host_id else "None"

    st.write(f"👑 Host: **{host_name}**")

    st.write("### Players")

    for p in players:
        pname = r.hget(f"user:{p}", "name") or p

        col1, col2 = st.columns([3, 1])

        with col1:
            label = f"🟢 {pname} (you)" if p == user_id else f"⚪ {pname}"
            if p == host_id:
                label += " 👑"
            st.write(label)

        with col2:
            # host-only kick
            if user_id == host_id and p != user_id:
                if st.button("❌ Kick", key=f"kick_{p}"):
                    r.srem(f"game:{game_id}:players", p)
                    st.rerun()

    # -------------------------
    # LEAVE GAME
    # -------------------------
    st.divider()

    if st.button("🚪 Leave Game"):
        r.srem(f"game:{game_id}:players", user_id)s
        # if host leaves, remove host
        if user_id == host_id:
            r.delete(f"game:{game_id}:host")
        del st.session_state.game_id
        st.rerun()
    # -------------------------
    # DELETE LOBBY (HOST ONLY)
    # -------------------------
    if user_id == host_id:
        confirm = st.checkbox("I understand this will reset the lobby")
        if st.button("Delete Lobby"):
            if confirm:
                r.delete(f"game:{game_id}:exists")
                r.delete(f"game:{game_id}:host")
                r.delete(f"game:{game_id}:players")
                del st.session_state.game_id
                st.rerun()