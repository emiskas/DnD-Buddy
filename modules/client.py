from discord import Client, Intents

# Set up Discord bot with required intents
intents: Intents = Intents.default()
intents.message_content = True
intents.voice_states = True
client: Client = Client(intents=intents)