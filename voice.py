import asyncio

import discord
import yt_dlp
from discord.utils import get

FFMPEG_OPTIONS = {"options": "-vn"}


async def play_soundcloud(vc, soundcloud_url):
    """Fetches and plays audio from a SoundCloud URL."""
    ydl_opts = {
        "format": "bestaudio",
        "extract_audio": True,
        "audio_format": "mp3",
        "quiet": True,  # Suppresses unnecessary console output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(soundcloud_url, download=False)
        url = info["url"]

    vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))

    # Wait for playback to finish before disconnecting
    while vc.is_playing():
        await asyncio.sleep(1)

    await vc.disconnect()  # Bot leaves voice channel after song ends


async def handle_voice_command(client, message):
    """Handles joining a voice channel and playing SoundCloud audio."""

    soundcloud_url = message.content.split(" ", 1)[1]  # Extract URL from message

    if not message.author.voice or not message.author.voice.channel:
        await message.channel.send("You need to be in a voice channel!")
        return

    voice_channel = message.author.voice.channel
    vc = get(client.voice_clients, guild=message.guild)

    if not vc:
        vc = await voice_channel.connect()

    await play_soundcloud(vc, soundcloud_url)
