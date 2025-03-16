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
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(soundcloud_url, download=False)
            url = info["url"]

        vc.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS))

        # Wait for playback to finish before disconnecting
        while vc.is_playing():
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Error playing audio: {e}")

    await vc.disconnect()


async def handle_voice_command(interaction, soundcloud_url):
    """Handles joining a voice channel and playing SoundCloud audio."""
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    vc = get(interaction.client.voice_clients, guild=interaction.guild)

    if not vc:
        vc = await voice_channel.connect()

    await interaction.response.send_message(f"🎶 Playing audio from: {soundcloud_url}")
    await play_soundcloud(vc, soundcloud_url)
