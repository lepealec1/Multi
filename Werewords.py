import streamlit as st
import redis, uuid, time, random
import os


# =========================
# UTIL
# =========================
def safe_decode(x):
    return x.decode() if isinstance(x, bytes) else x


# =========================
# SELECT MAYOR (HOST ONLY)
# =========================
def SelectMayor(r, user_id, game_id):

    host_id = safe_decode(r.get(f"game:{game_id}:host"))
    if user_id != host_id:
        return

    player_ids = r.smembers(f"game:{game_id}:players")
    players = []
    id_to_name = {}

    for pid in player_ids:
        pid = safe_decode(pid)

        name = r.hget(f"user:{pid}", "name")
        name = safe_decode(name)

        if not name:
            name = pid

        players.append(name)
        id_to_name[name] = pid

    if not players:
        return

    current = st.session_state.get(f"mayor_{game_id}", players[0])

    selected_name = st.selectbox(
        "Select Mayor",
        players,
        index=players.index(current) if current in players else 0,
        key=f"mayor_select_{game_id}"
    )

    selected_id = id_to_name[selected_name]

    r.set(f"game:{game_id}:mayor", selected_id)
    st.session_state[f"mayor_{game_id}"] = selected_name

    return selected_id


# =========================
# SETUP GAME
# =========================
def StartSetup(r, user_id, game_id):

    host = safe_decode(r.get(f"game:{game_id}:host"))
    if host != user_id:
        return

    player_ids = list(r.smembers(f"game:{game_id}:players"))
    player_count = len(player_ids)

    if player_count < 4:
        st.warning("Need at least 4 players")
        return

    st.subheader("⚙ Setup Game")

    col1, col2 = st.columns(2)
    with col1:
        minutes = st.number_input("Minutes", 0, 60, 5, key=f"{game_id}_min")
    with col2:
        seconds = st.number_input("Seconds", 0, 59, 0, key=f"{game_id}_sec")

    seer = st.number_input("Seer", 0, player_count - 2, 1, key=f"{game_id}_seer")
    werewolves = st.number_input("Werewolves", 1, player_count - 3, 1, key=f"{game_id}_wolf")

    mayor = 1
    villagers = player_count - (mayor + seer + werewolves)

    if villagers < 0:
        st.error("Invalid roles")
        return

    if st.button("Save Setup", key=f"{game_id}_save"):

        r.hset(f"game:{game_id}:settings", mapping={
            "timer_seconds": int(minutes * 60 + seconds),
            "seer": seer,
            "werewolves": werewolves,
            "villagers": villagers
        })

        r.set(f"game:{game_id}:state", "ready")
        st.success("Game ready!")


# =========================
# RUN GAME (ROLE ASSIGNMENT)
# =========================
def RunGame(r, user_id, game_id):

    if not r.get(f"game:{game_id}:run_requested"):
        return

    host = safe_decode(r.get(f"game:{game_id}:host"))
    if user_id != host:
        return

    r.delete(f"game:{game_id}:run_requested")

    # -------------------------
    # LOCK STATE
    # -------------------------
    r.set(f"game:{game_id}:state", "started")

    # -------------------------
    # PLAYERS
    # -------------------------
    player_ids = [safe_decode(p) for p in r.smembers(f"game:{game_id}:players")]

    if len(player_ids) < 4:
        return

    # -------------------------
    # SETTINGS
    # -------------------------
    settings = r.hgetall(f"game:{game_id}:settings")
    settings = {safe_decode(k): safe_decode(v) for k, v in settings.items()}

    seer = int(settings.get("seer", 0))
    werewolves = int(settings.get("werewolves", 0))

    # -------------------------
    # MAYOR (LOCKED)
    # -------------------------
    mayor_id = safe_decode(r.get(f"game:{game_id}:mayor"))
    if not mayor_id:
        st.error("Mayor not selected")
        return

    # remove mayor from pool
    player_ids = [p for p in player_ids if p != mayor_id]

    random.shuffle(player_ids)

    # -------------------------
    # ROLE ASSIGNMENT
    # -------------------------
    roles = {mayor_id: "Mayor"}
    idx = 0

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

    # -------------------------
    # WORD LIST
    # -------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    WORDS_PATH = os.path.join(BASE_DIR, "words.txt")

    with open(WORDS_PATH, "r") as f:
        words = [w.strip() for w in f if w.strip()]

    mayor_words = random.sample(words, min(10, len(words)))

    r.delete(f"game:{game_id}:mayor_words")
    for w in mayor_words:
        r.rpush(f"game:{game_id}:mayor_words", w)

    st.rerun()


# =========================
# MAYOR WORD PICK
# =========================
def MayorSelectWord(r, user_id, game_id):

    state = safe_decode(r.get(f"game:{game_id}:state"))
    if state != "started":
        return

    role = safe_decode(r.hget(f"game:{game_id}:roles", user_id))
    if role != "Mayor":
        return

    words = [safe_decode(w) for w in r.lrange(f"game:{game_id}:mayor_words", 0, -1)]

    st.subheader("👑 Pick Secret Word")

    chosen = st.selectbox("Word", words)

    col1, col2 = st.columns(2)

    if col1.button("Lock Word"):
        r.set(f"game:{game_id}:secret_word", chosen)
        r.set(f"game:{game_id}:state", "word_selected")
        st.rerun()

    if col2.button("Re-roll"):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        WORDS_PATH = os.path.join(BASE_DIR, "words.txt")

        with open(WORDS_PATH, "r") as f:
            all_words = [w.strip() for w in f if w.strip()]

        new_words = random.sample(all_words, min(10, len(all_words)))

        r.delete(f"game:{game_id}:mayor_words")
        for w in new_words:
            r.rpush(f"game:{game_id}:mayor_words", w)

        st.rerun()


# =========================
# REVEAL ROLES
# =========================
import streamlit as st

def RevealRoles(r, user_id, game_id):

    state = safe_decode(r.get(f"game:{game_id}:state"))

    if state != "word_selected":
        return

    # -------------------------
    # SAFE ROLE FETCH (FIXED BUG)
    # -------------------------
    role = get_role(r, game_id, user_id)

    secret = safe_decode(r.get(f"game:{game_id}:secret_word"))

    st.subheader("🎭 Your Role")

    if not role:
        st.error("Role not found (debug: check Redis role assignment)")
        return

    st.write(f"Role: **{role}**")

    # -------------------------
    # SEER
    # -------------------------
    if role == "Seer":
        st.info("🔮 You are the Seer")
        st.write("Hint system active")
        st.write(f"Word length: {len(secret)}")

    # -------------------------
    # WEREWOLF
    # -------------------------
    elif role == "Werewolf":
        st.warning("🐺 You are a Werewolf")

        players = r.hgetall(f"game:{game_id}:roles")
        wolves = [
            safe_decode(pid)
            for pid, rrole in players.items()
            if safe_decode(rrole) == "Werewolf"
        ]

        st.write("Other Werewolves:")
        st.write(wolves)

    # -------------------------
    # VILLAGER
    # -------------------------
    elif role == "Villager":
        st.success("👤 You are a Villager")
        st.write("Figure out the word!")

    # -------------------------
    # DEBUG MODE (OPTIONAL)
    # -------------------------
    elif role == "Mayor":
        st.info("👑 Mayor View")
        st.write("SECRET WORD (debug only):")
        st.error(secret)





def get_role(r, game_id, user_id):
    user_id = safe_decode(user_id).strip()

    raw = r.hget(f"game:{game_id}:roles", user_id)
    return safe_decode(raw) if raw else None
# =========================
# TIMER
# =========================
def RenderTimer(r, user_id, game_id):

    data = r.hgetall(f"game:{game_id}:timer")
    if not data:
        return

    start = float(safe_decode(data[b"start_time"]))
    duration = int(safe_decode(data[b"duration"]))

    remaining = int(duration - (time.time() - start))

    if remaining <= 0:
        r.set(f"game:{game_id}:state", "ended")
        st.error("Time up!")
        return

    st.subheader(f"⏱ {remaining//60:02d}:{remaining%60:02d}")


# =========================
# RUN BUTTON
# =========================
def RenderRunGameButton(r, user_id, game_id):

    state = safe_decode(r.get(f"game:{game_id}:state"))
    host = safe_decode(r.get(f"game:{game_id}:host"))

    if host != user_id:
        return

    disabled = state != "ready"

    if st.button("▶ Run Game", disabled=disabled):
        r.set(f"game:{game_id}:run_requested", 1)
        st.rerun()