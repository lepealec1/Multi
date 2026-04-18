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
        st.session_state.name = name.strip().lower()

    display_name = st.session_state.name if st.session_state.name else user_id

    r.hset(f"user:{user_id}", "name", display_name)

    st.write(f"👤 You are: **{display_name}**")

    return user_id, display_name

def render_lobby(r, user_id):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id

    st.divider()
    st.subheader(f"🎮 Lobby: {game_id}")

    host_id = r.get(f"game:{game_id}:host")

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

                    # remove player
                    r.srem(f"game:{game_id}:players", p)

                    # ALSO remove their name
                    pname = r.hget(f"user:{p}", "name")
                    if pname:
                        r.srem(f"game:{game_id}:player_names", pname)

                    st.rerun()

def leave_game(r, user_id):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    host_id = r.get(f"game:{game_id}:host")

    if st.button("🚪 Leave Game"):
        r.srem(f"game:{game_id}:players", user_id)

        name = r.hget(f"user:{user_id}", "name")
        if name:
            r.srem(f"game:{game_id}:player_names", name)

        if user_id == host_id:
            r.delete(f"game:{game_id}:host")

        del st.session_state.game_id
        st.rerun()
import streamlit as st

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

                user_id = st.session_state.user_id
                name = st.session_state.get("name", "").strip().lower()

                name_key = f"game:{game_id}:player_names"

                # 🚨 enforce unique names
                if r.sismember(name_key, name):
                    st.error("That name is already taken in this lobby.")
                else:
                    r.sadd(f"game:{game_id}:players", user_id)
                    r.sadd(name_key, name)

                    st.session_state.game_id = game_id
                    st.rerun()

        # -------------------------
        # ADMIN DELETE BUTTON
        # -------------------------
        if is_admin:
            if st.button("🗑", key=f"del_{game_id}"):

                r.delete(f"game:{game_id}:exists")
                r.delete(f"game:{game_id}:host")
                r.delete(f"game:{game_id}:players")
                r.delete(f"game:{game_id}:player_names")

                st.success(f"Deleted {game_id}")
                st.rerun()

                

def delete_lobby(r, user_id):
    if "game_id" not in st.session_state:
        return

    game_id = st.session_state.game_id
    host_id = r.get(f"game:{game_id}:host")

    # only host can delete
    if user_id != host_id:
        return

    st.divider()
    st.subheader("⚠️ Delete Lobby")

    confirm = st.checkbox("I understand this will permanently delete the lobby")

    if st.button("🗑 Delete Lobby"):
        if not confirm:
            st.error("You must confirm before deleting.")
            return

        # delete all game data
        r.delete(f"game:{game_id}:exists")
        r.delete(f"game:{game_id}:host")
        r.delete(f"game:{game_id}:players")
        r.delete(f"game:{game_id}:player_names")

        # remove session state
        if "game_id" in st.session_state:
            del st.session_state.game_id

        st.success("Lobby deleted.")
        st.rerun()
def refresh_button(label="🔄 Refresh"):
    if st.button(label):
        st.rerun()
