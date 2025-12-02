#  ____            _     _
# |  _ \  ___  ___(_)___(_) ___  _ __
# | | | |/ _ \/ __| / __| |/ _ \| '_ \
# | |_| |  __/ (__| \__ \ | (_) | | | |
# |____/ \___|\___|_|___/_|\___/|_| |_|
#


def make_decision(scored: list) -> tuple:
    if not scored: return False, 0, None

    best  = max(scored, key=lambda x: x["score"])
    score = best["score"]

    if score >= 0.90: return True, score, best["candidate"]
    else: return False, score, None


if __name__ == '__main__':
    pass
