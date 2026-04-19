def safe_decode(x):
    return x.decode() if isinstance(x, bytes) else x


def norm(x):
    return safe_decode(x).strip()


