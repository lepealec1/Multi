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

import streamlit as st

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

    if r.get(f"game:{game_id}:state") == b"started":
        st.success("Game already started.")
        return

    st.write(f"Players: **{player_count}**")

    col1, col2 = st.columns(2)
    with col1:
        minutes = st.number_input("Minutes", 0, 60, 5, key=f"{game_id}_min")
    with col2:
        seconds = st.number_input("Seconds", 0, 59, 0, step=15, key=f"{game_id}_sec")

    st.divider()
    st.write("### Roles")

    seer = st.number_input("Seer", 0, player_count - 1, 1, key=f"{game_id}_seer")
    werewolves = st.number_input("Werewolves", 1, player_count - 2, 1, key=f"{game_id}_wolf")

    mayor = 1
    villagers = player_count - (mayor + seer + werewolves)

    st.write(f"Mayor: **1 (fixed)**")
    st.write(f"Villagers (auto): **{villagers}**")

    if villagers < 0:
        st.error("Too many special roles.")
        return

    if (mayor + seer + werewolves + villagers) != player_count:
        st.error("Role mismatch.")
        return

    if st.button("Save Setup", key=f"{game_id}_save"):

        r.hset(f"game:{game_id}:settings", mapping={
            "timer_seconds": int(minutes * 60 + seconds),
            "mayor": 1,
            "seer": seer,
            "werewolves": werewolves,
            "villagers": villagers
        })

        # ✅ THIS IS WHAT YOUR BUTTON CHECKS FOR
        r.set(f"game:{game_id}:state", "ready")

        st.success("Setup saved. Game is ready.")
        
        

def safe_decode(x):
    return x.decode() if isinstance(x, bytes) else x


def RunGame(r, user_id, game_id):

    # must be setup first
    if not r.get(f"game:{game_id}:setup_ready"):
        return

    # already started
    if r.get(f"game:{game_id}:state") == b"started":
        st.info("Game already running.")
        return

    # 🔒 ONLY RUN IF HOST CLICKED BUTTON
    run_requested = r.get(f"game:{game_id}:run_requested")
    if not run_requested:
        return  # silently do nothing

    host = safe_decode(r.get(f"game:{game_id}:host"))

    # only host can trigger run
    if host != user_id:
        st.warning("Only host can start the game.")
        return

    # clear request so it doesn't rerun
    r.delete(f"game:{game_id}:run_requested")

    # get players
    player_ids = [safe_decode(p) for p in r.smembers(f"game:{game_id}:players")]

    if len(player_ids) < 4:
        st.error("Not enough players.")
        return

    # settings
    raw_settings = r.hgetall(f"game:{game_id}:settings")

    settings = {}
    for k, v in raw_settings.items():
        settings[safe_decode(k)] = safe_decode(v)

    seer = int(settings.get("seer", 0))
    werewolves = int(settings.get("werewolves", 0))

    random.shuffle(player_ids)

    roles = {}
    idx = 0

    roles[player_ids[idx]] = "Mayor"
    idx += 1

    for _ in range(seer):
        if idx < len(player_ids):
            roles[player_ids[idx]] = "Seer"
            idx += 1

    for _ in range(werewolves):
        if idx < len(player_ids):
            roles[player_ids[idx]] = "Werewolf"
            idx += 1

    for i in range(idx, len(player_ids)):
        roles[player_ids[i]] = "Villager"

    for pid, role in roles.items():
        r.hset(f"game:{game_id}:roles", pid, role)

    r.set(f"game:{game_id}:state", "started")

    st.success("Game started!")
    st.rerun()



import streamlit as st

import streamlit as st

import streamlit as st

import streamlit as st

def RenderRunGameButton(r, user_id, game_id):

    state = r.get(f"game:{game_id}:state")
    state = state.decode() if isinstance(state, bytes) else state

    host = r.get(f"game:{game_id}:host")
    host = host.decode() if isinstance(host, bytes) else host

    # only host sees button
    if host != user_id:
        return

    # DEBUG (keep this until working)
    st.write("STATE:", state)

    # button ALWAYS visible for host
    disabled = (state != "ready")

    if st.button("▶ Run Game", disabled=disabled):

        r.set(f"game:{game_id}:run_requested", 1)
        st.rerun()



def RunGame(r, user_id, game_id):

    # must be requested
    if not r.get(f"game:{game_id}:run_requested"):
        return

    host = safe_decode(r.get(f"game:{game_id}:host"))

    if host != user_id:
        return

    # clear request so it doesn't rerun
    r.delete(f"game:{game_id}:run_requested")

    # set state
    r.set(f"game:{game_id}:state", "started")

    # -------------------------
    # LOAD PLAYERS
    # -------------------------
    player_ids = [safe_decode(p) for p in r.smembers(f"game:{game_id}:players")]

    random.shuffle(player_ids)

    if len(player_ids) < 4:
        st.error("Not enough players.")
        return

    # -------------------------
    # LOAD SETTINGS
    # -------------------------
    settings = r.hgetall(f"game:{game_id}:settings")

    settings = {
        safe_decode(k): safe_decode(v)
        for k, v in settings.items()
    }

    seer = int(settings.get("seer", 0))
    werewolves = int(settings.get("werewolves", 0))

    # -------------------------
    # LOAD WORD LIST
    # -------------------------
    with open("words.txt", "r") as f:
        words = [line.strip() for line in f if line.strip()]

    mayor_words = random.sample(words, min(10, len(words)))

    # -------------------------
    # ROLE ASSIGNMENT
    # -------------------------
    roles = {}

    idx = 0

    # Mayor first
    mayor_id = player_ids[idx]
    roles[mayor_id] = "Mayor"
    idx += 1

    # Seer
    for _ in range(seer):
        if idx < len(player_ids):
            roles[player_ids[idx]] = "Seer"
            idx += 1

    # Werewolves
    for _ in range(werewolves):
        if idx < len(player_ids):
            roles[player_ids[idx]] = "Werewolf"
            idx += 1

    # Villagers
    for i in range(idx, len(player_ids)):
        roles[player_ids[i]] = "Villager"

    # -------------------------
    # STORE ROLES
    # -------------------------
    for pid, role in roles.items():
        r.hset(f"game:{game_id}:roles", pid, role)

    # -------------------------
    # STORE MAYOR WORD LIST
    # -------------------------
    r.delete(f"game:{game_id}:mayor_words")
    for w in mayor_words:
        r.rpush(f"game:{game_id}:mayor_words", w)

    st.success("Game started! Roles assigned + words loaded.")
    st.rerun()


import streamlit as st

def safe_decode(x):
    return x.decode() if isinstance(x, bytes) else x


def RevealRoles(r, user_id, game_id):

    state = safe_decode(r.get(f"game:{game_id}:state"))

    if state != "word_selected":
        return

    role = safe_decode(r.hget(f"game:{game_id}:roles", user_id))
    secret_word = safe_decode(r.get(f"game:{game_id}:secret_word"))

    st.subheader("🎭 Your Role")

    st.write(f"**Role:** {role}")

    # -------------------------
    # MAYOR (knows word list)
    # -------------------------
    if role == "Mayor":
        words = r.lrange(f"game:{game_id}:mayor_words", 0, -1)
        words = [safe_decode(w) for w in words]

        st.write("🎯 Choose the secret word:")
        st.write(words)

    # -------------------------
    # SEER (gets hint)
    # -------------------------
    elif role == "Seer":
        st.info("🔮 You are the Seer")
        st.write("You may see a hint about the word.")

        # simple hint (first/last letter or length)
        st.write(f"Word length: {len(secret_word)}")

    # -------------------------
    # WEREWOLVES (group info)
    # -------------------------
    elif role == "Werewolf":
        st.warning("🐺 You are a Werewolf")
        st.write("Work with other werewolves to guess the word.")

        # show fellow wolves
        players = r.hgetall(f"game:{game_id}:roles")

        wolves = [
            safe_decode(pid)
            for pid, rrole in players.items()
            if safe_decode(rrole) == "Werewolf"
        ]

        st.write("Other Werewolves:")
        st.write(wolves)

    # -------------------------
    # VILLAGERS
    # -------------------------
    else:
        st.success("👤 You are a Villager")
        st.write("Try to figure out the word!")


def RenderTimer(r, user_id, game_id):

    data = r.hgetall(f"game:{game_id}:timer")
    if not data:
        return

    start_time = float(safe_decode(data[b"start_time"]))
    duration = int(safe_decode(data[b"duration"]))

    elapsed = time.time() - start_time
    remaining = int(duration - elapsed)

    if remaining <= 0:
        r.set(f"game:{game_id}:state", "ended")
        st.error("⏰ Time's up!")
        st.stop()

    mins = remaining // 60
    secs = remaining % 60

    st.subheader(f"⏱ Time Left: {mins:02d}:{secs:02d}")
    


def MayorSelectWord(r, user_id, game_id):

    state = safe_decode(r.get(f"game:{game_id}:state"))

    if state != "started":
        return

    role = safe_decode(r.hget(f"game:{game_id}:roles", user_id))

    if role != "Mayor":
        return

    words = r.lrange(f"game:{game_id}:mayor_words", 0, -1)
    words = [safe_decode(w) for w in words]

    st.subheader("👑 Choose the Secret Word")

    chosen = st.selectbox("Pick a word", words)

    if st.button("Lock In Word"):

        r.set(f"game:{game_id}:secret_word", chosen)
        r.set(f"game:{game_id}:state", "word_selected")

        st.success("Word locked in!")
        st.rerun()


