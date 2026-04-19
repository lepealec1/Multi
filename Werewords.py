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
        seconds = st.number_input(
            "Seconds",
            min_value=0,
            max_value=59,
            value=0,
            step=15,
            key=f"{game_id}_sec"
        )
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
# MAYOR WORD PICK
def MayorSelectWord(r, user, game_id):
    state = r.get(f"game:{game_id}:state")

    if state != "ready":
        return

    mayor = r.get(f"game:{game_id}:mayor")

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

    state = r.get(f"game:{game_id}:state")
    if state != "word_selected":
        return

    # get role
    role = r.hget(f"game:{game_id}:roles", user)
    def get_roles(r, game_id):
        roles = r.hgetall(f"game:{game_id}:roles")

        return {
            (k.decode() if isinstance(k, bytes) else k):
            (v.decode() if isinstance(v, bytes) else v)
            for k, v in roles.items()
        }
    def get_werewolves(r, game_id):
        roles = get_roles(r, game_id)
        return [player for player, role in roles.items() if role == "Werewolf"]
    def get_seers(r, game_id):
        roles = get_roles(r, game_id)
        return [player for player, role in roles.items() if role == "Seer"]
    def get_villagers(r, game_id):
        roles = get_roles(r, game_id)
        return [player for player, role in roles.items() if role == "Villager"]
    werewolves = get_werewolves(r, game_id)
    seers = get_seers(r, game_id)
    villagers=get_villagers(r,game_id)
    if not role:
        st.write("No role assigned")
        return
    if role == "Werewolf":
        st.success("🐺🌕 You are a Werewolf.")
        if len(werewolves)==1:
            st.warning("You are the lone werewolf.")
        if len(werewolves)>1:
            st.warning(f"🐺 These are all the werewolves: {', '.join(werewolves)}")
    elif role == "Seer":
        st.success("🔮👁 You are a seer.")
        if len(seers)==1:
            st.warning("You are the lone seer.")
        if len(werewolves)>1:
            st.warning(f"🔮 These are all the seers: {', '.join(seers)}")
    elif role == "Villager":
        st.success("🏡👤 You are a villager.")
        st.warning(f"Including you, there are {len(villagers)} villagers.")
    elif role == "Mayor":
        st.success("🏡👤🏡👤 You are the mayor")
        st.warning(f"There are {len(villagers)} villagers.")


    # 👇 ONLY certain roles see the secret
    if role in ["Werewolf", "Seer", "Mayor"]:
        secret_word = r.get(f"game:{game_id}:secret_word")
        if secret_word:
            st.error(f"🔑 Secret word: {secret_word}")
        else:
            st.write("No secret set yet")
    if role in ["Villager"]:
        st.write("Try to guess the secret word")
       
    st.warning(f"Public: there are {len(werewolves)} werewolves.")
             



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


###
# Mayor Word Select + Pause Timer
###
def MayorButtons(r, user, game_id):
    state = r.get(f"game:{game_id}:state")
    if state != "word_selected":
        return
    mayor = r.get(f"game:{game_id}:mayor")
    if user != mayor:
        return
    if st.button("Secret word discovered!", key=f"{game_id}_discovered"):
        r.set(f"game:{game_id}:state", "paused")
        secret_word = r.get(f"game:{game_id}:secret_word")
        st.warning("Secrete word discovered.")
        st.warning("Werewolves vote to discover the seer.")
        st.warning(f"Secret word:",secret_word)
    st.rerun()
