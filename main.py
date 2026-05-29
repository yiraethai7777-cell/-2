import os
import random
import discord
from discord.ext import commands
from discord import app_commands

# ===== TOKEN =====
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("TOKEN 환경변수가 설정되지 않았습니다.")

# ===== INTENTS =====
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== DATA =====
balances = {}

OWNER_ID = 1503121370945683626
admins = {OWNER_ID}


# ===== UTIL =====
def is_admin(user_id: int):
    return user_id in admins


# ===== READY =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} 로그인 완료!")


# ===== 방장 =====
@bot.tree.command(name="방장", description="방장 확인")
async def owner(interaction: discord.Interaction):
    await interaction.response.send_message("공주")


# ===== 관리자 임명 =====
@bot.tree.command(name="관리자임명", description="관리자 임명")
@app_commands.describe(유저="관리자로 만들 사람")
async def add_admin(interaction: discord.Interaction, 유저: discord.User):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("방장만 가능합니다.", ephemeral=True)
        return

    admins.add(유저.id)

    await interaction.response.send_message(f"{유저.name} 님이 관리자가 되었습니다.")


# ===== 돈 지급 (초기 지급) =====
@bot.tree.command(name="돈줘", description="10만원 지급")
async def give_start_money(interaction: discord.Interaction):

    user_id = interaction.user.id

    if user_id in balances:
        await interaction.response.send_message("이미 지급받았습니다.", ephemeral=True)
        return

    balances[user_id] = 100000

    await interaction.response.send_message("10만원 지급 완료!")


# ===== 돈 확인 =====
@bot.tree.command(name="돈", description="잔액 확인")
async def check_money(interaction: discord.Interaction):

    money = balances.get(interaction.user.id, 0)

    await interaction.response.send_message(f"현재 잔액: {money:,}원")


# ===== 관리자 돈 지급 =====
@bot.tree.command(name="돈지급", description="관리자 전용 돈 지급")
@app_commands.describe(유저="지급 대상", 금액="지급 금액")
async def give_money(interaction: discord.Interaction, 유저: discord.User, 금액: int):

    if not is_admin(interaction.user.id):
        await interaction.response.send_message("관리자 전용 명령어입니다.", ephemeral=True)
        return

    if 금액 <= 0:
        await interaction.response.send_message("금액은 1 이상이어야 합니다.", ephemeral=True)
        return

    balances[유저.id] = balances.get(유저.id, 0) + 금액

    await interaction.response.send_message(f"{유저.name} 님에게 {금액:,}원 지급 완료!")


# ===== 도박 =====
@bot.tree.command(name="도박", description="도박 게임")
@app_commands.describe(금액="도박할 금액")
async def gamble(interaction: discord.Interaction, 금액: int):

    user_id = interaction.user.id
    balance = balances.get(user_id, 0)

    if 금액 <= 0:
        await interaction.response.send_message("1원 이상 입력하세요.", ephemeral=True)
        return

    if balance < 금액:
        await interaction.response.send_message("잔액 부족!", ephemeral=True)
        return

    # 1% 잭팟
    if random.randint(1, 100) == 1:
        reward = 금액 * 5
        balances[user_id] = balances.get(user_id, 0) + reward

        await interaction.response.send_message(f"🎉 JACKPOT!!!\n{reward:,}원 획득!")
        return

    result = random.choice(["win", "lose"])

    if result == "win":
        balances[user_id] = balances.get(user_id, 0) + 금액
        await interaction.response.send_message(f"승리!\n{금액:,}원 획득!")

    else:
        balances[user_id] = balances.get(user_id, 0) - 금액
        await interaction.response.send_message(f"패배...\n{금액:,}원 잃음!")


# ===== 랭킹 =====
@bot.tree.command(name="랭킹", description="돈 랭킹 확인")
async def ranking(interaction: discord.Interaction):

    if not balances:
        await interaction.response.send_message("아직 데이터가 없습니다.")
        return

    sorted_users = sorted(balances.items(), key=lambda x: x[1], reverse=True)
    top = sorted_users[:10]

    msg = "🏆 **돈 랭킹 TOP 10**\n\n"

    for i, (user_id, money) in enumerate(top, start=1):

        user = interaction.guild.get_member(user_id)

        if user is None:
            user = await bot.fetch_user(user_id)

        name = getattr(user, "name", "알 수 없음")

        msg += f"{i}. {name} - {money:,}원\n"

    await interaction.response.send_message(msg)


# ===== RUN =====
bot.run(TOKEN)