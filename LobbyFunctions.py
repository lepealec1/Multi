import streamlit as st
import redis, uuid, time
import Functions

import streamlit as st
import uuid
def init_user(r):

    if "name" not in st.session_state:
        st.session_state.name = ""

    # -------------------------
    # INPUT
    # -------------------------
    name = st.text_input("Enter your name", value=st.session_state.name)

    if not name:
        st.write("👤 Enter a name to continue")
        return None, None

    name = name.strip()
    st.session_state.name = name

    user_id = name  # 👈 NAME IS THE ID

    # -------------------------
    # LOAD FROM REDIS
    # -------------------------
    existing = r.hget(f"user:{user_id}", "name")
    existing = Functions.safe_decode(existing)

    # if exists → load it
    if existing:
        st.session_state.user = user_id
    else:
        # create new user record
        r.hset(f"user:{user_id}", mapping={
            "name": name
        })
        st.session_state.user = user_id

    # -------------------------
    # UI CONTROLS
    # -------------------------
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Reload User"):
            # force re-read from Redis
            st.session_state.user = name
            st.rerun()

    with col2:
        if st.button("🆕 Switch Name"):
            st.session_state.name = ""
            st.session_state.user = None
            st.rerun()

    st.write(f"👤 You are: **{name}**")

    return user_id, name


def create_game(r, user):
    st.subheader("Create Game")

    # 🚫 BLOCK if already in a lobby
    if "game_id" in st.session_state:
        st.warning(f"You're already in lobby: {st.session_state.game_id}")
        return

    game_id = st.text_input("Game ID to create")

    if st.button("Create Game"):
        if game_id:
            r.set(f"game:{game_id}:exists", 1)
            r.set(f"game:{game_id}:host", user)
            r.sadd(f"game:{game_id}:players", user)

            st.session_state.game_id = game_id
            st.rerun()
        else:
            st.error("Enter a Game ID")



def render_lobby(r, user):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id

    st.divider()
    st.subheader(f"🎮 Lobby: {game_id}")

    host_id = r.get(f"game:{game_id}:host")
    r.sadd(f"game:{game_id}:players", user)

    players = list(r.smembers(f"game:{game_id}:players"))

    host_name = r.hget(f"user:{host_id}", "name") if host_id else "None"
    st.write(f"Host: **{host_name}**")

    st.write("### Players")

    for p in players:
        pname = r.hget(f"user:{p}", "name") or p

        col1, col2 = st.columns([3, 1])

        with col1:
            label = f"🟢 {pname} (you)" if p == user else f"⚪ {pname}"
            if p == host_id:
                label += " 👑"
            st.write(label)

        with col2:
            if user == host_id and p != user:
                if st.button("❌ Remove", key=f"kick_{p}"):
                    r.srem(f"game:{game_id}:players", p)
                    st.rerun()



def leave_game(r, user):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    host_id = r.get(f"game:{game_id}:host")

    if st.button("🚪 Leave Game"):
        r.srem(f"game:{game_id}:players", user)

        if user == host_id:
            r.delete(f"game:{game_id}:host")

        del st.session_state.game_id
        st.rerun()



def delete_lobby(r, user):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    host_id = r.get(f"game:{game_id}:host")

    if user != host_id:
        return

    confirm = st.checkbox("I understand this will reset the lobby")

    if st.button("Delete Lobby"):
        if confirm:
            r.delete(f"game:{game_id}:exists")
            r.delete(f"game:{game_id}:host")
            r.delete(f"game:{game_id}:players")

            del st.session_state.game_id
            st.rerun()
            


def view_lobbies(r):
    st.subheader("🌐 Active Lobbies")

    display_name = st.session_state.get("name", "")
    is_admin = (display_name == "alepe")

    keys = r.keys("game:*:exists")

    if not keys:
        st.write("No active lobbies")
        return

    for key in keys:
        game_id = key.split(":")[1]

        host_id = r.get(f"game:{game_id}:host")
        host_name = r.hget(f"user:{host_id}", "name") if host_id else "None"

        # 👇 PLAYER COUNT (THIS IS THE KEY ADDITION)
        player_count = r.scard(f"game:{game_id}:players")

        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

        with col1:
            st.write(f"🎮 **{game_id}**")

        with col2:
            st.write(f"👑 {host_name}")

        with col3:
            st.write(f"👥 {player_count}")

        with col4:
            if st.button("Join", key=f"join_{game_id}"):
                st.session_state.game_id = game_id
                r.sadd(f"game:{game_id}:players", st.session_state.user)
                st.rerun()

        # -------------------------
        # ADMIN DELETE BUTTON
        # -------------------------
        if is_admin:
            if st.button("🗑", key=f"del_{game_id}"):
                r.delete(f"game:{game_id}:exists")
                r.delete(f"game:{game_id}:host")
                r.delete(f"game:{game_id}:players")
                r.srem("active_lobbies", game_id)

                st.success(f"Deleted {game_id}")
                st.rerun()


def refresh_button(label="🔄 Refresh"):
    if st.button(label):
        st.rerun()

def SelectGame(r, user, game_id):

    host = (r.get(f"game:{game_id}:host"))

    if user != host:
        return

    options = ["None", "Werewords"]

    current = Functions.safe_decode(r.get(f"game:{game_id}:mode")) or "None"

    if st.button("Set Werewords Mode"):
        r.set(f"game:{game_id}:mode", "Werewords")
        st.success("Game mode set to Werewords")
        st.rerun()


def reset_roles_button(r, user, game_id):
    host_id = r.get(f"game:{game_id}:host")

    # only host can reset
    if user != host_id:
        return

    if st.button("🔄 Reset Roles"):
        r.delete(f"game:{game_id}:roles_assigned")
        r.delete(f"game:{game_id}:roles_lock")   # if using lock
        r.delete(f"game:{game_id}:roles")

        st.success("Roles reset!")
        r.set(f"game:{game_id}:state", "lobby")
        st.rerun()
                