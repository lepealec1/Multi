import streamlit as st
import redis
import json
import uuid
r = redis.Redis(
    host=st.secrets["REDIS_HOST"],
    port=int(st.secrets["REDIS_PORT"]),
    password=st.secrets["REDIS_PASSWORD"],
    ssl=True,   # IMPORTANT for Redis Cloud
    decode_responses=True
)

# test connection
r.ping()
st.success("Redis connected ✅")
# -------------------------
# HELPERS
# -------------------------
def get_room(room_id):
    data = r.get(f"room:{room_id}")
    return json.loads(data) if data else None

def save_room(room_id, data):
    r.set(f"room:{room_id}", json.dumps(data))

# -------------------------
# INIT UI
# -------------------------
st.title("🎮 Redis Multiplayer Lobby")

mode = st.radio("Mode", ["Create Room", "Join Room"])

# -------------------------
# CREATE ROOM
# -------------------------
if mode == "Create Room":
    if st.button("Create Room"):
        room_id = str(uuid.uuid4())[:6]

        room_data = {
            "players": []
        }

        save_room(room_id, room_data)

        st.success("Room created!")
        st.code(room_id)

# -------------------------
# JOIN ROOM
# -------------------------
if mode == "Join Room":
    room_id = st.text_input("Room Code")
    name = st.text_input("Your Name")

    if st.button("Join"):
        room = get_room(room_id)

        if not room:
            st.error("Room not found")
        else:
            if name not in room["players"]:
                room["players"].append(name)
                save_room(room_id, room)

            st.success(f"{name} joined {room_id}")

# -------------------------
# VIEW ROOM
# -------------------------
st.divider()

room_view = st.text_input("View Room Code")

if room_view:
    room = get_room(room_view)

    if room:
        st.subheader("👥 Players in Room")
        st.write(room["players"])
    else:
        st.warning("Room not found")