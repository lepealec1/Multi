import streamlit as st
import redis, uuid, time



def init_user(r):
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]

    user_id = st.session_state.user_id

    if "name" not in st.session_state:
        st.session_state.name = ""

    name = st.text_input("Enter your name", value=st.session_state.name)

    if name:
        st.session_state.name = name

    display_name = st.session_state.name if st.session_state.name else user_id

    r.hset(f"user:{user_id}", "name", display_name)

    st.write(f"👤 You are: **{display_name}**")

    return user_id, display_name


import streamlit as st

def create_game(r, user_id):
    st.subheader("Create Game")

    game_id = st.text_input("Game ID to create")

    if st.button("Create Game"):
        if game_id:
            r.set(f"game:{game_id}:exists", 1)
            r.set(f"game:{game_id}:host", user_id)
            r.sadd(f"game:{game_id}:players", user_id)

            st.session_state.game_id = game_id
            st.rerun()
        else:
            st.error("Enter a Game ID")

import streamlit as st

def join_game(r, user_id):
    st.subheader("Join Game")

    join_id = st.text_input("Game ID to join")

    if st.button("Join Game"):
        if r.exists(f"game:{join_id}:exists"):
            r.sadd(f"game:{join_id}:players", user_id)
            st.session_state.game_id = join_id
            st.rerun()
        else:
            st.error("Game not found")


import streamlit as st

def render_lobby(r, user_id):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id

    st.divider()
    st.subheader(f"🎮 Lobby: {game_id}")

    host_id = r.get(f"game:{game_id}:host")
    r.sadd(f"game:{game_id}:players", user_id)

    players = list(r.smembers(f"game:{game_id}:players"))

    host_name = r.hget(f"user:{host_id}", "name") if host_id else "None"
    st.write(f"Host: **{host_name}**")

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
            if user_id == host_id and p != user_id:
                if st.button("❌ Remove", key=f"kick_{p}"):
                    r.srem(f"game:{game_id}:players", p)
                    st.rerun()

import streamlit as st

def leave_game(r, user_id):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    host_id = r.get(f"game:{game_id}:host")

    if st.button("🚪 Leave Game"):
        r.srem(f"game:{game_id}:players", user_id)

        if user_id == host_id:
            r.delete(f"game:{game_id}:host")

        del st.session_state.game_id
        st.rerun()

import streamlit as st

def delete_lobby(r, user_id):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    host_id = r.get(f"game:{game_id}:host")

    if user_id != host_id:
        return

    confirm = st.checkbox("I understand this will reset the lobby")

    if st.button("Delete Lobby"):
        if confirm:
            r.delete(f"game:{game_id}:exists")
            r.delete(f"game:{game_id}:host")
            r.delete(f"game:{game_id}:players")

            del st.session_state.game_id
            st.rerun()
            