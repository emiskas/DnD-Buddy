import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from modules.responses import setup as setup_responses
from modules import voice  # For setting the main loop

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ✅ Initialize the bot
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"✅ {client.user} is now running!")

    try:
        setup_responses(client)
        synced = await client.tree.sync()
        print(f"✅ Synced {len(synced)} command(s) successfully!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@client.event
async def on_disconnect():
    print(f"🚫 {client.user} has disconnected")

@client.event
async def on_resumed():
    print(f"🔄 {client.user} has reconnected")

# ✅ Start the bot inside a running event loop
async def main():
    # Set the main loop reference for voice.py
    voice.main_loop = asyncio.get_running_loop()
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
