import os
from random import randint
import discord
from discord import app_commands, Interaction
import google.generativeai as genai
from dotenv import load_dotenv
from .initiative_tracker import InitiativeTracker
from modules.voice import (
    handle_single_video_command,
    handle_playlist_command,
    audio_queue
)

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

    # DICE ROLL
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

    # INITIATIVE ROLL
    @app_commands.command(name="rollinit", description="Roll initiative with your dexterity modifier.")
    async def roll_init(self, interaction: Interaction, dex_modifier: int):
        d20 = randint(1, 20)
        initiative = d20 + dex_modifier
        name = interaction.user.name
        init_tracker.add_player(name, initiative)
        status = " Dayum, lucky." if initiative > 20 else " Oof." if initiative < 10 else ""
        embed = discord.Embed(
            title="🎯 Initiative Roll",
            description=f"**{name}** rolled **{initiative}**{status}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Rolled with a D20 + Dex modifier ({dex_modifier})")
        await interaction.response.send_message(embed=embed)

    # INITIATIVE ORDER
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

    # INITIATIVE RESET
    @app_commands.command(name="initreset", description="Reset the initiative order.")
    async def init_reset(self, interaction: Interaction):
        init_tracker.reset()
        embed = discord.Embed(
            title="♻️ Initiative Reset",
            description="Initiative order has been reset.",
            color=discord.Color.purple()
        )
        await interaction.response.send_message(embed=embed)

    # LUNA AI
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

    # MUSIC: PLAY VIDEO
    @app_commands.command(name="play", description="Play a single YouTube video.")
    async def play(self, interaction: Interaction, url: str):
        await handle_single_video_command(interaction, url)

    # MUSIC: PLAY PLAYLIST
    @app_commands.command(name="playlist", description="Play a YouTube playlist.")
    async def playlist(self, interaction: Interaction, url: str):
        await handle_playlist_command(interaction, url)

    # MUSIC: SHOW QUEUE
    @app_commands.command(name="queue", description="Show the current song queue.")
    async def queue(self, interaction: Interaction):
        if not audio_queue:
            await interaction.response.send_message("📭 The queue is currently empty.", ephemeral=True)
            return
        upcoming = list(audio_queue)
        limited = upcoming[:10]
        desc = "\n".join([f"{i+1}. {title}" for i, (title, _) in enumerate(limited)])
        if len(upcoming) > 10:
            desc += f"\n\n...and {len(upcoming) - 10} more in queue."
        embed = discord.Embed(
            title="🎶 Current Queue",
            description=desc,
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)

    # MUSIC: PAUSE
    @app_commands.command(name="pause", description="Pause the current song.")
    async def pause(self, interaction: Interaction):
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Paused playback.")
        else:
            await interaction.response.send_message("⚠️ No track is currently playing.", ephemeral=True)

    # MUSIC: RESUME
    @app_commands.command(name="resume", description="Resume paused music.")
    async def resume(self, interaction: Interaction):
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Resumed playback.")
        else:
            await interaction.response.send_message("⚠️ Nothing is paused right now.", ephemeral=True)

    # MUSIC: SKIP
    @app_commands.command(name="skip", description="Skip the currently playing song.")
    async def skip(self, interaction: Interaction):
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped the current track.")
        else:
            await interaction.response.send_message("⚠️ No track is currently playing.", ephemeral=True)

    # MUSIC: STOP & CLEAR
    @app_commands.command(name="stop", description="Stop playback and disconnect.")
    async def stop(self, interaction: Interaction):
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
        if vc:
            audio_queue.clear()
            await vc.disconnect()
            await interaction.response.send_message("🛑 Stopped playback and disconnected.")
        else:
            await interaction.response.send_message("⚠️ I'm not in a voice channel.", ephemeral=True)

    # COMMAND LIST
    @app_commands.command(name="commands", description="Display all available commands.")
    async def commands(self, interaction: Interaction):
        embed = discord.Embed(
            title="📜 Available Commands",
            description="Here's what I can do:",
            color=discord.Color.gold()
        )
        embed.add_field(name="🎲 `/dnd roll <dice>`", value="Roll a dice (d4, d6, etc).", inline=False)
        embed.add_field(name="🎯 `/dnd rollinit <dex_mod>`", value="Roll initiative for combat.", inline=False)
        embed.add_field(name="🏆 `/dnd order`", value="Show initiative order.", inline=False)
        embed.add_field(name="♻️ `/dnd initreset`", value="Reset initiative order.", inline=False)
        embed.add_field(name="🧙 `/dnd ask <question>`", value="Ask Luna about D&D rules.", inline=False)
        embed.add_field(name="▶️ `/dnd play <url>`", value="Play a single YouTube video.", inline=False)
        embed.add_field(name="📀 `/dnd playlist <url>`", value="Queue a YouTube playlist.", inline=False)
        embed.add_field(name="⏸️ `/dnd pause`", value="Pause music.", inline=False)
        embed.add_field(name="▶️ `/dnd resume`", value="Resume music.", inline=False)
        embed.add_field(name="⏭️ `/dnd skip`", value="Skip the current track.", inline=False)
        embed.add_field(name="🧾 `/dnd queue`", value="Show upcoming songs.", inline=False)
        embed.add_field(name="🛑 `/dnd stop`", value="Stop and disconnect.", inline=False)
        await interaction.response.send_message(embed=embed)

def setup(client):
    client.tree.add_command(Responses(name="dnd"))