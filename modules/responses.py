import os
from random import choice, randint
import discord
import google.generativeai as genai
from dotenv import load_dotenv
from .client import client
from .initiative_tracker import InitiativeTracker

init_tracker = InitiativeTracker()

load_dotenv()
KEY = os.getenv("AI_API_KEY")
genai.configure(api_key=KEY)


SYSTEM_MESSAGE = (
    "You are a knowledgeable and helpful D&D guide named Luna. "
    "You are an expert in Dungeons & Dragons (5e) rules, mechanics, and lore, aswell as homebrew stuff "
    "You only answer questions about character creation, combat, spells, and game mechanics. "
    "Respond in a medieval, mystical tone and keep responses brief and helpful unless it asks about specific rules or spells and how they work."
)

def get_response(user_input: str) -> str:
    lowered: str = user_input.content.lower()

    if lowered.startswith("!"):
        if lowered[1:] in ("d4", "d6", "d8", "d10", "d12", "d20"):
            roll = randint(1, int(lowered[2:]))
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"You rolled: **{roll}**",
                color=discord.Color.green()
            )
            return embed

        # Handle initiative rolls (NOW USING EMBED)
        elif lowered.startswith("!rollinit"):
            if not lowered[10:].isdigit():
                embed = discord.Embed(
                    title="⚠️ Error",
                    description="You need to provide your dexterity modifier.",
                    color=discord.Color.red()
                )
                return embed

            name = user_input.author.name
            d20 = randint(1, 20)
            dex_modifier = int(lowered[10:])
            initiative = d20 + dex_modifier
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

            return embed

        elif lowered == "!order":
            init_tracker.sort_initiative()
            order = init_tracker.display_order()

            embed = discord.Embed(
                title="🏆 Initiative Order",
                description=order,
                color=discord.Color.gold()
            )
            embed.set_footer(text="Sorted by highest initiative first")
            return embed

        elif lowered == "!initreset":
            init_tracker.reset()
            embed = discord.Embed(
                title="♻️ Initiative Reset",
                description="Initiative order has been reset.",
                color=discord.Color.purple()
            )
            return embed
        
        elif lowered.startswith("!ask"):
            prompt = user_input.content[5:].strip()

            if not prompt:
                embed = discord.Embed(
                    title="⚠️ Error",
                    description="You need to ask a question, traveler!",
                    color=discord.Color.red()
                )
                return embed

            try:
                model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
                response = model.generate_content(f"{SYSTEM_MESSAGE}\nUser: {prompt}")
                reply = response.text.strip()

                embed = discord.Embed(
                    title="🧙 Luna's Wisdom",
                    description=reply,
                    color=discord.Color.teal()
                )
                embed.set_footer(text=f"Requested by {user_input.author.name}")
                return embed

            except Exception as e:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: `{e}`",
                    color=discord.Color.red()
                )
                return embed

        # Handle unknown commands (fallback)
        else:
            embed = discord.Embed(
                title="🤔 Huh?",
                description=choice(["Da hell O _ o", "Uhh whut", "Mhm mhm (I don't get it)"]),
                color=discord.Color.orange()
            )
            return embed

    return None  # Return None to ensure non-command messages don't trigger unnecessary responses
