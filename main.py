import os

from discord import Client, Intents, Message
from dotenv import load_dotenv

from modules.responses import get_response
from modules.voice import handle_voice_command

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up Discord bot with required intents
intents: Intents = Intents.default()
intents.message_content = True
intents.voice_states = True
client: Client = Client(intents=intents)


async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("(message was empty because intents were not enabled)")
        return

    if is_private := user_message[0] == "?":
        user_message = user_message[1:]

    response: str = get_response(user_message)
    if response:
        (
            await message.author.send(response)
            if is_private
            else await message.channel.send(response)
        )


@client.event
async def on_ready() -> None:
    print(f"{client.user} is now running")


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    # Check if message starts with !play and call handle_voice_command instead of handling voice logic here
    if user_message.startswith("!play "):
        await handle_voice_command(client, message)
        return  # Prevents text response after playing audio

    await send_message(message, user_message)


def main() -> None:
    client.run(TOKEN)


if __name__ == "__main__":
    main()
