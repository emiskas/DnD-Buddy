import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from modules.responses import setup as setup_responses

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ✅ Initialize the bot
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

# -------------------------------
# ✅ Register Slash Commands
# -------------------------------
@client.event
async def on_ready():
    print(f"✅ {client.user} is now running!")

    try:
        # Register responses (DND commands)
        setup_responses(client)

        # Sync all commands with Discord
        synced = await client.tree.sync()
        print(f"✅ Synced {len(synced)} command(s) successfully!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# -------------------------------
# ✅ Clean up Shutdown Handling
# -------------------------------
@client.event
async def on_disconnect():
    print(f"🚫 {client.user} has disconnected")

@client.event
async def on_resumed():
    print(f"🔄 {client.user} has reconnected")

# -------------------------------
# ✅ Start the Bot
# -------------------------------
def main():
    client.run(TOKEN)

if __name__ == "__main__":
    main()
