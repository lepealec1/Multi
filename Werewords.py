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
import random

def StartSetup(r, user_id, game_id):

    players_key = f"game:{game_id}:players"
    player_ids = list(r.smembers(players_key))
    player_count = len(player_ids)

    player_ids = [
        p.decode() if isinstance(p, bytes) else p
        for p in player_ids
    ]

    if player_count < 4:
        st.warning("Need at least 4 players to start Werewords.")
        return

    host = r.get(f"game:{game_id}:host")
    if host:
        host = host.decode() if isinstance(host, bytes) else host

    if host != user_id:
        st.info("Waiting for host...")
        return

    # prevent reopening after final start
    if r.get(f"game:{game_id}:state") == b"started":
        st.success("Game already started.")
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

        seer = st.number_input("Seer", 0, player_count - 1, 1)
        werewolves = st.number_input("Werewolves", 1, player_count - 2, 1)

        mayor = 1  # fixed

        villagers = player_count - (mayor + seer + werewolves)

        st.write(f"Mayor: **1 (fixed)**")
        st.write(f"Villagers (auto): **{villagers}**")

        if villagers < 0:
            st.error("Too many special roles.")
            return

        total = mayor + seer + werewolves + villagers

        if total != player_count:
            st.error("Roles must equal total players.")
            return

        # Save setup but DO NOT start game yet
        if st.button("Save Setup"):

            r.hset(f"game:{game_id}:settings", mapping={
                "timer_seconds": int(minutes * 60 + seconds),
                "mayor": 1,
                "seer": seer,
                "werewolves": werewolves,
                "villagers": villagers
            })

            r.set(f"game:{game_id}:setup_ready", 1)

            st.success("Setup saved. Ready to start game!")

        # 🔥 RUN GAME BUTTON (separate step)
        if r.get(f"game:{game_id}:setup_ready"):

            if st.button("▶ Run Game"):

                random.shuffle(player_ids)

                roles = {}

                roles[player_ids[0]] = "Mayor"
                idx = 1

                for _ in range(seer):
                    roles[player_ids[idx]] = "Seer"
                    idx += 1

                for _ in range(werewolves):
                    roles[player_ids[idx]] = "Werewolf"
                    idx += 1

                for i in range(idx, player_count):
                    roles[player_ids[i]] = "Villager"

                for pid, role in roles.items():
                    r.hset(f"game:{game_id}:roles", pid, role)

                r.set(f"game:{game_id}:state", "started")

                st.success("Game started! Roles assigned.")
                st.rerun()

    setup()