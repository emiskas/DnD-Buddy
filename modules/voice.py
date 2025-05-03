import asyncio
from collections import deque
from urllib.parse import urlparse, parse_qs
import discord
import yt_dlp

# Shared queue and event loop
audio_queue = deque()
main_loop = None
playing_lock = asyncio.Lock()

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

def extract_playlist_url(raw_url: str) -> str | None:
    parsed = urlparse(raw_url)
    query = parse_qs(parsed.query)
    playlist_id = query.get("list", [None])[0]
    if playlist_id:
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    return None

async def play_next(vc: discord.VoiceClient):
    async with playing_lock:
        if not audio_queue:
            print("📭 Queue is empty. Disconnecting...")
            await vc.disconnect()
            return

        title, url = audio_queue.popleft()
        print(f"🎵 Now playing: {title}")

        try:
            ydl_opts = {
                "format": "bestaudio",
                "quiet": True,
                "no_warnings": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info["url"]

            def after_playing(error):
                if error:
                    print(f"❌ Playback error: {error}")
                fut = asyncio.run_coroutine_threadsafe(play_next(vc), main_loop)
                try:
                    fut.result()
                except Exception as e:
                    print(f"❌ After playback error: {e}")

            source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
            vc.play(source, after=after_playing)

        except Exception as e:
            print(f"❌ FFmpeg failed to play: {e}")
            await play_next(vc)

async def handle_single_video_command(interaction: discord.Interaction, url: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return

    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel
    vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
    if not vc:
        vc = await voice_channel.connect()

    try:
        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': 'in_playlist'}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown")
            print(f"📥 Queued single video: {title} -> {url}")
            audio_queue.append((title, url))

        await interaction.followup.send(f"📥 Queued: **{title}**")

        if not vc.is_playing() and not vc.is_paused():
            await play_next(vc)

    except Exception as e:
        print(f"⚠️ Failed to fetch video info: {e}")
        await interaction.followup.send("❌ Failed to play video.", ephemeral=True)

async def handle_playlist_command(interaction: discord.Interaction, url: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You need to be in a voice channel!", ephemeral=True)
        return

    await interaction.response.defer()

    playlist_url = extract_playlist_url(url)
    if not playlist_url:
        await interaction.followup.send("⚠️ Invalid playlist URL.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
    if not vc:
        vc = await voice_channel.connect()

    try:
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': False
        }) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

            if "entries" not in info or not info["entries"]:
                await interaction.followup.send("⚠️ No entries found in playlist.", ephemeral=True)
                return

            entries = info["entries"]
            for i, entry in enumerate(entries):
                if not entry:
                    continue
                title = entry.get("title", f"Track {i+1}")
                entry_url = f"https://www.youtube.com/watch?v={entry['id']}"
                if i == 0 and not vc.is_playing() and not vc.is_paused():
                    print(f"📥 Queued first: {title} -> {entry_url}")
                    audio_queue.appendleft((title, entry_url))
                    await play_next(vc)
                else:
                    print(f"📥 Queued (bg): {title} -> {entry_url}")
                    audio_queue.append((title, entry_url))

            await interaction.followup.send(f"✅ Added {len(entries)} tracks to the queue.")

    except Exception as e:
        print(f"⚠️ Playlist error: {e}")
        await interaction.followup.send("❌ Failed to queue playlist.", ephemeral=True)
