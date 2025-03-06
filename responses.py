from random import choice, randint

# -- Space for ChatGPT --


def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered.startswith("!"):
        if lowered[1:] in ("d4", "d6", "d8", "d10", "d12", "d20"):
            return f"You rolled: {randint(1, int(lowered[2:]))}"
        else:
            return choice(["da hell O _ o", "uhh whut", "mhm mhm (I don't get it)"])

    return None  # Return None to ensure non-command messages don't trigger unnecessary responses
