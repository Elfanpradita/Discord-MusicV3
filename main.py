import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from music.player import MusicPlayer

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)
players = {}

def get_player(guild_id):
    if guild_id not in players:
        players[guild_id] = MusicPlayer()
    return players[guild_id]

@bot.event
async def on_ready():
    print(f'✅ Bot aktif sebagai {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if not voice_client or not voice_client.is_connected():
        return

    if len(voice_client.channel.members) == 1:
        await asyncio.sleep(10)
        if len(voice_client.channel.members) == 1:
            await voice_client.disconnect()
            print(f"📤 Bot keluar otomatis dari {voice_client.channel.name} karena kosong.")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        player = get_player(ctx.guild.id)
        player.voice_client = await channel.connect()
        await ctx.send(f"✅ Bergabung ke {channel.name}")
    else:
        await ctx.send("❗ Kamu harus join voice channel dulu.")

@bot.command()
async def play(ctx, *, query):
    player = get_player(ctx.guild.id)
    if not ctx.author.voice:
        await ctx.send("❗ Kamu harus join voice channel dulu.")
        return
    if not player.voice_client or not player.voice_client.is_connected():
        await ctx.invoke(bot.get_command("join"))
    await player.add_song(query)
    await ctx.send("🎵 Lagu ditambahkan ke antrian.")
    await player.start_playing(ctx)

@bot.command()
async def skip(ctx):
    player = get_player(ctx.guild.id)
    player.skip()
    await ctx.send("⏭️ Skip lagu.")

@bot.command()
async def pause(ctx):
    player = get_player(ctx.guild.id)
    player.pause()
    await ctx.send("⏸️ Lagu dipause.")

@bot.command()
async def resume(ctx):
    player = get_player(ctx.guild.id)
    player.resume()
    await ctx.send("▶️ Lagu dilanjut.")

@bot.command()
async def stop(ctx):
    player = get_player(ctx.guild.id)
    player.stop()
    await ctx.send("⏹️ Musik dihentikan dan antrian dihapus.")

@bot.command()
async def queue(ctx):
    player = get_player(ctx.guild.id)
    q = player.get_queue()
    if not q:
        await ctx.send("📭 Antrian kosong.")
    else:
        msg = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(q)])
        await ctx.send(f"📜 Antrian saat ini:\n{msg}")

@bot.command(name="nowplaying", aliases=["np"])
async def nowplaying(ctx):
    player = get_player(ctx.guild.id)
    if player.current:
        await ctx.send(f"🎧 Sekarang memutar: **{player.current['title']}**")
    else:
        await ctx.send("⏸️ Tidak ada lagu yang sedang diputar.")

@bot.command()
async def clear(ctx):
    player = get_player(ctx.guild.id)
    player.clear_queue()
    await ctx.send("🗑️ Antrian dikosongkan.")

@bot.command()
async def remove(ctx, index: int):
    player = get_player(ctx.guild.id)
    if player.remove_at(index - 1):
        await ctx.send(f"❌ Lagu nomor {index} dihapus dari antrian.")
    else:
        await ctx.send("🚫 Nomor lagu tidak valid.")

@bot.command()
async def leave(ctx):
    player = get_player(ctx.guild.id)
    if player.voice_client:
        await player.voice_client.disconnect()
        await ctx.send("📤 Bot keluar dari voice channel.")

# ✅ WAJIB UNTUK JALANKAN BOT
if __name__ == "__main__":
    bot.run(TOKEN)
