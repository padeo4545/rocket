import discord
import random
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # .envからトークンを読み込み

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.guilds = True
intents.message_content = True  # ✅ 追加！

bot = commands.Bot(command_prefix="/", intents=intents)

# グローバル変数：待機順管理用
wait_queue = []

# ✅ /wake 2 または /wake 3 でチーム分け
@bot.command()
async def wake(ctx, team_size: int = 2):
    if team_size not in [2, 3]:
        await ctx.send("チーム人数は2人または3人で指定してください！")
        return

    vc = ctx.author.voice
    if not vc:
        await ctx.send("まずVCに参加してから使ってください！")
        return

    members = [member for member in vc.channel.members if not member.bot]
    random.shuffle(members)

    num_teams = len(members) // team_size
    teams = [members[i*team_size:(i+1)*team_size] for i in range(num_teams)]

    result = ""
    for i, team in enumerate(teams, start=1):
        names = " ".join([member.display_name for member in team])
        result += f"チーム{i}: {names}\n"

    leftovers = members[num_teams*team_size:]
    if leftovers:
        extra = " ".join([member.display_name for member in leftovers])
        result += f"\n未振り分け: {extra}"

    await ctx.send(result)

# ✅ /next_match で 2vs2 + 待機者表示（5人想定、順番ローテーション）
@bot.command()
async def nextm(ctx):
    vc = ctx.author.voice
    if not vc:
        await ctx.send("まずVCに参加してから使ってください！")
        return

    members = [member for member in vc.channel.members if not member.bot]
    if len(members) < 5:
        await ctx.send("5人以上がVCに参加している必要があります！")
        return

    global wait_queue

    # 初回だけシャッフルして待機順を決定
    if not wait_queue:
        wait_queue = members.copy()
        random.shuffle(wait_queue)

    # 待機者 = キューの先頭
    waiter = wait_queue.pop(0)

    # 残りで2チーム構成
    active_members = [m for m in members if m != waiter]
    random.shuffle(active_members)
    team1 = active_members[:2]
    team2 = active_members[2:]

    result = f"⏸️ 待機者: {waiter.display_name}\n"
    result += f"🎯 チームA: {team1[0].display_name}, {team1[1].display_name}\n"
    result += f"🔥 チームB: {team2[0].display_name}, {team2[1].display_name}"

    # 待機者を末尾に戻す（順番ローテーション）
    wait_queue.append(waiter)

    await ctx.send(result)

bot.run(TOKEN)