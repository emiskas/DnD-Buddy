from random import choice, randint

from .client import client
from .initiative_tracker import InitiativeTracker

init_tracker = InitiativeTracker()

# -- Space for ChatGPT --


def get_response(user_input: str) -> str:
    lowered: str = user_input.content.lower()

    if lowered.startswith("!"):
        if lowered[1:] in ("d4", "d6", "d8", "d10", "d12", "d20"):
            return f"You rolled: {randint(1, int(lowered[2:]))}"

        elif lowered.startswith("!rollinit"):
            print(lowered[10:])
            if not lowered[10:].isdigit():
                return "You need to provide your dexterity modifier"

            name = user_input.author.name

            d20 = randint(1, 20)
            dex_modifier = lowered[10:]

            initiative = d20 + int(dex_modifier)
            init_tracker.add_player(name, initiative)

            if initiative > 20:
                return f"Your initiative is: {initiative}. Dayum, lucky."

            elif initiative < 10:
                return f"Your initiative is: {initiative}. Oof"

            return f"Your initiative is: {initiative}"

        elif lowered == "!order":
            init_tracker.sort_initiative()

            return init_tracker.display_order()

        elif lowered == "!initreset":
            return "Initiative order has been reset."

        else:
            return choice(["Da hell O _ o", "Uhh whut", "Mhm mhm (I don't get it)"])

    return None  # Return None to ensure non-command messages don't trigger unnecessary responses
