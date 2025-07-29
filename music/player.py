import asyncio
import yt_dlp
import discord

ytdl_format_options = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class MusicPlayer:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.current = None
        self.voice_client = None
        self.playing_task = None

    async def add_song(self, query):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        url = data['url']
        title = data['title']
        return await self.queue.put({'title': title, 'url': url})

    async def start_playing(self, ctx):
        if self.playing_task is None or self.playing_task.done():
            self.playing_task = asyncio.create_task(self._play_loop(ctx))

    async def _play_loop(self, ctx):
        while not self.queue.empty():
            self.current = await self.queue.get()
            source = discord.FFmpegPCMAudio(self.current['url'], **ffmpeg_options)
            self.voice_client.play(source)
            await ctx.send(f"🎶 Memutar: **{self.current['title']}**")
            while self.voice_client.is_playing() or self.voice_client.is_paused():
                await asyncio.sleep(1)
        self.current = None

    def skip(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()

    def pause(self):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()

    def resume(self):
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()

    def stop(self):
        if self.voice_client:
            self.voice_client.stop()
            self.queue = asyncio.Queue()
            self.current = None

    def get_queue(self):
        return list(self.queue._queue)

    def clear_queue(self):
        self.queue = asyncio.Queue()

    def remove_at(self, index):
        q = list(self.queue._queue)
        if 0 <= index < len(q):
            del q[index]
            self.queue._queue.clear()
            self.queue._queue.extend(q)
            return True
        return False
