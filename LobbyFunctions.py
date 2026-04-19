import streamlit as st
import redis, uuid, time
import Functions 

import streamlit as st
import uuid

def init_user(r):

    # --- SESSION USER ID ---
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    # --- NAME INPUT ---
    name = st.text_input("Enter your name", value=st.session_state.get("name", ""))

    if name:
        name = name.strip()
        st.session_state.name = name

        # 🔍 LOOK FOR EXISTING USER WITH THIS NAME
        keys = r.keys("user:*")

        found_user_id = None

        for key in keys:
            user_id = key.split(":")[1]

            stored_name = r.hget(f"user:{user_id}", "name")
            stored_name = stored_name.decode() if isinstance(stored_name, bytes) else stored_name

            if stored_name == name:
                found_user_id = user_id
                break

        # ✅ EXISTING USER → LOAD IT
        if found_user_id:
            st.session_state.user_id = found_user_id

        # 🆕 NEW USER → CREATE IT
        else:
            new_id = str(uuid.uuid4())[:8]
            st.session_state.user_id = new_id

            r.hset(f"user:{new_id}", mapping={
                "name": name
            })

    # fallback display id
    user_id = st.session_state.user_id or "unknown"

    display_name = st.session_state.name.strip() if st.session_state.name else user_id

    st.write(f"👤 You are: **{display_name}**")

    return user_id, display_name


def create_game(r, user_id):
    st.subheader("Create Game")

    # 🚫 BLOCK if already in a lobby
    if "game_id" in st.session_state:
        st.warning(f"You're already in lobby: {st.session_state.game_id}")
        return

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
                r.sadd(f"game:{game_id}:players", st.session_state.user_id)
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
def SelectGame(r, user_id, game_id):

    host_id = Functions.safe_decode(r.get(f"game:{game_id}:host"))

    if user_id != host_id:
        return

    options = ["None", "Werewords"]

    current = Functions.safe_decode(r.get(f"game:{game_id}:mode")) or "None"

    mode = st.radio(
        "Select Game Mode",
        options,
        index=options.index(current) if current in options else 0,
        key=f"game_mode_{game_id}"
    )

    if st.button("Set Game Mode"):
        r.set(f"game:{game_id}:mode", mode)
        st.success(f"Game mode set to {mode}")
        st.rerun()