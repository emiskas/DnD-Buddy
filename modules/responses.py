import os
from random import choice, randint
import discord
from discord import app_commands, Interaction
import google.generativeai as genai
from dotenv import load_dotenv
from .initiative_tracker import InitiativeTracker
from .voice import handle_voice_command

init_tracker = InitiativeTracker()

load_dotenv()
KEY = os.getenv("AI_API_KEY")
genai.configure(api_key=KEY)

SYSTEM_MESSAGE = (
    "You are a knowledgeable and helpful D&D guide named Luna. "
    "You are an expert in Dungeons & Dragons (5e) rules, mechanics, and lore, as well as homebrew content. "
    "You only answer questions about character creation, combat, spells, and game mechanics. "
    "Respond in a medieval, mystical tone and keep responses brief and helpful unless it asks about specific rules or spells and how they work."
)

class Responses(app_commands.Group):

    # 🎲 Dice Roll Command
    @app_commands.command(name="roll", description="Roll a dice (d4, d6, d8, d10, d12, d20).")
    async def roll(self, interaction: Interaction, dice: str):
        if dice not in ["d4", "d6", "d8", "d10", "d12", "d20"]:
            await interaction.response.send_message("Invalid dice type! Use d4, d6, d8, d10, d12, or d20.", ephemeral=True)
            return

        roll = randint(1, int(dice[1:]))
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled: **{roll}**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    # 🎯 Roll Initiative Command
    @app_commands.command(name="rollinit", description="Roll initiative with your dexterity modifier.")
    async def roll_init(self, interaction: Interaction, dex_modifier: int):
        d20 = randint(1, 20)
        initiative = d20 + dex_modifier
        name = interaction.user.name

        init_tracker.add_player(name, initiative)
        status = ""
        if initiative > 20:
            status = " Dayum, lucky."
        elif initiative < 10:
            status = " Oof."

        embed = discord.Embed(
            title="🎯 Initiative Roll",
            description=f"**{name}** rolled **{initiative}** {status}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Rolled with a D20 + Dex modifier ({dex_modifier})")

        await interaction.response.send_message(embed=embed)

    # 🏆 Display Initiative Order Command
    @app_commands.command(name="order", description="Display the current initiative order.")
    async def order(self, interaction: Interaction):
        init_tracker.sort_initiative()
        order = init_tracker.display_order()

        embed = discord.Embed(
            title="🏆 Initiative Order",
            description=order,
            color=discord.Color.gold()
        )
        embed.set_footer(text="Sorted by highest initiative first")

        await interaction.response.send_message(embed=embed)

    # ♻️ Reset Initiative Command
    @app_commands.command(name="initreset", description="Reset the initiative order.")
    async def init_reset(self, interaction: Interaction):
        init_tracker.reset()
        embed = discord.Embed(
            title="♻️ Initiative Reset",
            description="Initiative order has been reset.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    # 🧙 Ask AI Command
    @app_commands.command(name="ask", description="Ask Luna a question about D&D.")
    async def ask(self, interaction: Interaction, question: str):
        if not question:
            await interaction.response.send_message("You need to ask a question, traveler!", ephemeral=True)
            return
        
        try:
            model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
            response = model.generate_content(f"{SYSTEM_MESSAGE}\nUser: {question}")
            reply = response.text.strip()

            embed = discord.Embed(
                title="🧙 Luna's Wisdom",
                description=reply,
                color=discord.Color.teal()
            )
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"An error occurred: `{e}`", ephemeral=True)

    # 📜 List All Commands
    @app_commands.command(name="commands", description="Display all available commands.")
    async def commands(self, interaction: Interaction):
        embed = discord.Embed(
            title="📜 Available Commands",
            description="Here are the commands you can use:",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎲 `/roll <dice>`", value="Roll a dice of the specified type.", inline=False)
        embed.add_field(name="🎯 `/rollinit <dex_mod>`", value="Roll initiative with your dexterity modifier.", inline=False)
        embed.add_field(name="🏆 `/order`", value="Display the current initiative order.", inline=False)
        embed.add_field(name="♻️ `/initreset`", value="Reset the initiative order.", inline=False)
        embed.add_field(name="🧙 `/ask <question>`", value="Ask Luna a question about D&D rules and mechanics.", inline=False)
        embed.add_field(name="🎶 `/play <url>`", value="Play audio from SoundCloud.", inline=False)

        embed.set_footer(text="May the dice roll ever in your favor!")
        await interaction.response.send_message(embed=embed)

    # 🎶 Play Command
    @app_commands.command(name="play", description="Play audio from SoundCloud")
    async def play(self, interaction: Interaction, url: str):
        await handle_voice_command(interaction, url)



# ✅ Register the Group
def setup(client):
    client.tree.add_command(Responses(name="dnd"))
