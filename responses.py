from random import choice, randint

from dice import dice

#place for chat gpt later

def get_response(user_input : str) -> str:
    lowered: str = user_input.lower()
    
    if lowered == '':
        return 'Well, you\'re awfully silent..'
    elif 'hello' in lowered:
        return 'Hello fleshling'
    elif lowered in dice:
        return f'you rolled: {randint(1, int(lowered[1:]))}'
    else:
        return choice(['da hell O _ o', 'uhh whut', 'mhm mhm(i don\'t get it)'])