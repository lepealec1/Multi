import streamlit as st
import redis, uuid, time

def SelectMayor(r, user_id, game_id):

    host_id = r.get(f"game:{game_id}:host")
    if isinstance(host_id, bytes):
        host_id = host_id.decode("utf-8")

    player_ids = r.smembers(f"game:{game_id}:players")

    players = []
    id_to_name = {}

    for pid in player_ids:
        pid = pid.decode("utf-8") if isinstance(pid, bytes) else pid

        # ✅ FIXED LINE (THIS IS THE BUG)
        name = r.hget(f"user:{pid}", "name")
        name = name.decode("utf-8") if isinstance(name, bytes) else name

        if not name:
            name = pid  # fallback so UI never shows None

        players.append(name)
        id_to_name[name] = pid

    if user_id != host_id:
        mayor_id = r.get(f"game:{game_id}:mayor")
        if isinstance(mayor_id, bytes):
            mayor_id = mayor_id.decode("utf-8")

        if not mayor_id:
            return None

        name = r.hget(f"user:{mayor_id}", "name")
        return name.decode("utf-8") if isinstance(name, bytes) else name

    if not players:
        return None

    if "mayor" not in st.session_state:
        st.session_state.mayor = players[0]

    selected_name = st.selectbox(
        "Select Mayor",
        players,
        index=players.index(st.session_state.mayor)
        if st.session_state.mayor in players else 0,
        key=f"mayor_{game_id}"
    )

    selected_id = id_to_name[selected_name]
    r.set(f"game:{game_id}:mayor", selected_id)

    st.session_state.mayor = selected_name

    return selected_name
import streamlit as st
import redis

def StartSetup(r, user_id, game_id):

    players_key = f"game:{game_id}:players"
    player_count = r.scard(players_key)

    # Must have at least 4 players
    if player_count < 4:
        st.warning("Need at least 4 players to start Werewords.")
        return

    # Only host can configure
    host = r.get(f"game:{game_id}:host")
    if host:
        host = host.decode() if isinstance(host, bytes) else host

    if host != user_id:
        st.info("Waiting for host to start setup...")
        return

    # prevent reopening multiple times
    if r.get(f"game:{game_id}:setup_done"):
        return

    @st.dialog("Werewords Setup")
    def setup():

        st.write(f"Players: **{player_count}**")

        col1, col2 = st.columns(2)
        with col1:
            minutes = st.number_input("Minutes", 0, 60, 5)
        with col2:
            seconds = st.number_input("Seconds", 0, 59, 0)

        st.divider()
        st.write("### Roles")

        mayor = st.number_input("Mayor", 0, player_count, 1)
        seer = st.number_input("Seer", 0, player_count, 1)
        werewolves = st.number_input("Werewolves", 1, player_count, 1)

        villagers = player_count - (mayor + seer + werewolves)

        st.write(f"Villagers (auto): **{villagers}**")

        total = mayor + seer + werewolves + villagers

        if villagers < 0:
            st.error("Too many special roles.")
            return

        if total != player_count:
            st.error("Roles must equal total players.")
            return

        if st.button("Start Game"):

            r.hset(f"game:{game_id}:settings", mapping={
                "timer_seconds": int(minutes * 60 + seconds),
                "mayor": int(mayor),
                "seer": int(seer),
                "werewolves": int(werewolves),
                "villagers": int(villagers)
            })

            r.set(f"game:{game_id}:state", "started")
            r.set(f"game:{game_id}:setup_done", 1)

            st.success("Game started!")
            st.rerun()

    setup()

'''
🐺 Main Roles
Mayor
Knows the secret word.
Can only answer yes / no / maybe questions.
Helps villagers guess the word (without being obvious).
Seer
Knows the secret word.
Tries to subtly guide players without revealing themselves.
Werewolves
Usually 1–2 players.
Know the secret word.
Try to mislead everyone so the word isn’t guessed in time.
Villagers
Most of the players.
Don’t know the word.
Ask questions to figure it out before time runs out.
'''
