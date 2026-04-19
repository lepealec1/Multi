import streamlit as st
import redis
import uuid
import time
import random
import os
import Functions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORDS_PATH = os.path.join(BASE_DIR, "Words.txt")

def load_words():
    with open(WORDS_PATH, "r") as f:
        return [w.strip() for w in f if w.strip()]
    
    
def get_role(r, game_id, user):

    raw = r.hget(f"game:{game_id}:roles", user) 
    return raw

# =========================
# MAYOR SELECTION
# =========================
def SelectMayor(r, user, game_id):

    host_id = (r.get(f"game:{game_id}:host"))
    if user != host_id:
        return

    raw_players = r.smembers(f"game:{game_id}:players")
    player_ids = [(p) for p in raw_players]

    players = []
    id_to_name = {}

    for pid in player_ids:

        if not pid:
            continue

        name = (r.hget(f"user:{pid}", "name"))

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

    r.set(f"game:{game_id}:mayor", selected_name)

    st.session_state[f"mayor_{game_id}"] = selected_name



# =========================
# SETUP
# =========================
def StartSetup(r, user, game_id):
    host = (r.get(f"game:{game_id}:host"))
    st.write("StartSetup:Host:",host)
    if host != user:
        return
    player_ids = [(p) for p in r.smembers(f"game:{game_id}:players")]
    player_count = len(player_ids)
    if player_count < 3:
        st.warning("Need at least 3 players")
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
        st.error("Invalid role setup")
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
        st.rerun()


# =========================
# RUN GAME
# =========================
def RunGame(r, user, game_id):

    if not r.get(f"game:{game_id}:run_requested"):
        return

    host = r.get(f"game:{game_id}:host")
    if user != host:
        return
    r.delete(f"game:{game_id}:run_requested")
    r.set(f"game:{game_id}:state", "started")
    player_ids = [(p) for p in r.smembers(f"game:{game_id}:players")]
    if len(player_ids) < 3:
        return
    # -------------------------
    # SETTINGS
    # -------------------------
    settings = {
        (k):(v)
        for k, v in r.hgetall(f"game:{game_id}:settings").items()
    }
    seer = int(settings.get("seer", 0))
    werewolves = int(settings.get("werewolves", 0))

    # -------------------------
    # MAYOR
    # -------------------------
    mayor_id =(r.get(f"game:{game_id}:mayor"))
    if not mayor_id:
        st.error("Mayor not set")
        return

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
        r.hset(f"game:{game_id}:roles", (pid), role)
    # -------------------------
    # WORDS
    # -------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    WORDS_PATH = os.path.join(BASE_DIR, "Words.txt")
    with open(WORDS_PATH, "r") as f:
        words = [w.strip() for w in f if w.strip()]
    mayor_words = random.sample(words, min(10, len(words)))
    r.delete(f"game:{game_id}:mayor_words")
    for w in mayor_words:
        r.rpush(f"game:{game_id}:mayor_words", w)
    st.rerun()
# =========================
# MAYOR WORD PICK
def MayorSelectWord(r, user, game_id):
    state = r.get(f"game:{game_id}:state")
    st.write("MayorSelectWord STATE:", state)

    if state != "ready":
        return

    mayor = r.get(f"game:{game_id}:mayor")
    st.write("RevealRoles Role:", mayor)

    if user != mayor:
        return

    words = r.lrange(f"game:{game_id}:mayor_words", 0, -1)
    words = [w.decode() if isinstance(w, bytes) else w for w in words]

    st.subheader("👑 Pick Secret Word")

    col1, col2 = st.columns(2)
    chosen = st.selectbox("Word", words)

    all_words = load_words()
    new_words = random.sample(all_words, min(10, len(all_words)))
    for w in new_words:
        r.rpush(f"game:{game_id}:mayor_words", w)

    if col1.button("Lock Word and Start Game"):
        r.set(f"game:{game_id}:secret_word", chosen)
        r.set(f"game:{game_id}:state", "word_selected")
        st.rerun()

    if col2.button("Randomize Words"):
        all_words = load_words()
        new_words = random.sample(all_words, min(10, len(all_words)))

        r.delete(f"game:{game_id}:mayor_words")
        for w in new_words:
            r.rpush(f"game:{game_id}:mayor_words", w)

        st.rerun()

# =========================
# REVEAL ROLES
# =========================
def RevealRoles(r, user, game_id):
    st.write("Revealing Roles")

    state = r.get(f"game:{game_id}:state")
    if state != "word_selected":
        return

    # get role
    role = r.hget(f"game:{game_id}:roles", user)

    if not role:
        st.write("No role assigned")
        return

    st.write(f"Your role: {role}")

    # 👇 ONLY certain roles see the secret
    if role in ["Werewolf", "Seer", "Mayor"]:
        secret_word = r.get(f"game:{game_id}:secret_word")

        if secret_word:
            st.write(f"🔑 Secret word: {secret_word}")
        else:
            st.write("No secret set yet")

# =========================
# TIMER
# =========================
def RenderTimer(r, user, game_id):

    data = r.hgetall(f"game:{game_id}:timer")
    if not data:
        return

    start = float((data.get(b"start_time", 0)))
    duration = int((data.get(b"duration", 0)))

    remaining = int(duration - (time.time() - start))

    if remaining <= 0:
        r.set(f"game:{game_id}:state", "ended")
        st.warning("Time up!")
        return

    st.subheader(f"⏱ {remaining//60:02d}:{remaining%60:02d}")


# =========================
# RUN BUTTON
# =========================
def RenderRunGameButton(r, user, game_id):
    state = (r.get(f"game:{game_id}:state"))
    secret = (r.get(f"game:{game_id}:secret_word")) or None
    mayor = (r.get(f"game:{game_id}:mayor"))
    if user != mayor:
        return
    can_start = (
        state == "ready"
        and secret is not None
        and secret != ""
        and secret.lower() != "none"
    )
    if st.button("▶ Run Game", disabled=not can_start):
        r.set(f"game:{game_id}:run_requested", 1)
        st.rerun()



def AssignRoles(r, user, game_id):
    host = r.get(f"game:{game_id}:host")
    if user != host:
        return

    # -------------------------
    # LOAD SETTINGS
    # -------------------------
    settings = r.hgetall(f"game:{game_id}:settings")
    settings = {k: v for k, v in settings.items()}

    seer_count = int(settings.get("seer", 0))
    werewolf_count = int(settings.get("werewolves", 0))

    # -------------------------
    # LOAD PLAYERS
    # -------------------------
    mayor = r.get(f"game:{game_id}:mayor")
    players = list(r.smembers(f"game:{game_id}:players"))

    # remove mayor from pool
    players = [p for p in players if p != mayor]

    if len(players) + 1 < 4:  # include mayor
        return "Not enough players"

    random.shuffle(players)

    roles = {}

    # -------------------------
    # KEEP ORIGINAL MAYOR
    # -------------------------
    roles[mayor] = "Mayor"

    idx = 0

    # -------------------------
    # SEER
    # -------------------------
    for _ in range(seer_count):
        if idx < len(players):
            roles[players[idx]] = "Seer"
            idx += 1

    # -------------------------
    # WEREWOLVES
    # -------------------------
    for _ in range(werewolf_count):
        if idx < len(players):
            roles[players[idx]] = "Werewolf"
            idx += 1

    # -------------------------
    # VILLAGERS
    # -------------------------
    for i in range(idx, len(players)):
        roles[players[i]] = "Villager"

    # -------------------------
    # SAVE TO REDIS
    # -------------------------
    r.delete(f"game:{game_id}:roles")

    for name, role in roles.items():
        r.hset(f"game:{game_id}:roles", name, role)
