st.write("=== ALL REDIS KEYS ===")
st.write(r.keys("*"))


st.subheader("🧠 FULL REDIS DUMP")

for key in r.keys("*"):

    key_str = Functions.safe_decode(key)
    value_type = r.type(key).decode() if isinstance(r.type(key), bytes) else r.type(key)

    st.write(f"### {key_str} ({value_type})")

    # STRING
    if value_type == "string":
        st.write(Functions.safe_decode(r.get(key)))

    # SET
    elif value_type == "set":
        st.write([Functions.safe_decode(x) for x in r.smembers(key)])

    # HASH
    elif value_type == "hash":
        raw = r.hgetall(key)
        st.write({
            Functions.safe_decode(k): Functions.safe_decode(v)
            for k, v in raw.items()
        })

    # LIST
    elif value_type == "list":
        st.write([Functions.safe_decode(x) for x in r.lrange(key, 0, -1)])
        