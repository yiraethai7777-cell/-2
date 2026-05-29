import os
import random
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "MTUwOTk4OTgzMTYxNzI4NjM5Ng.GV-RWa.WIO33f5oHMIcOmF9r1R5Aj84zcNR9NkCLuRFaY"
intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== 데이터 =====

balances = {}
games = {}

# 방장 ID 입력
OWNER_ID = 1503121370945683626
admins = {OWNER_ID}

# ===== 함수 =====

def is_admin(user_id):
    return user_id in admins

# ===== 실행 =====

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
async def add_admin(
    interaction: discord.Interaction,
    유저: discord.User
):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "방장만 가능합니다.",
            ephemeral=True
        )
        return

    admins.add(유저.id)

    await interaction.response.send_message(
        f"{유저.name} 님이 관리자가 되었습니다."
    )

# ===== 돈줘 =====

@bot.tree.command(name="돈줘", description="10만원 지급")
async def money_start(interaction: discord.Interaction):

    user_id = interaction.user.id

    if user_id in balances:
        await interaction.response.send_message(
            "이미 지급받았습니다.",
            ephemeral=True
        )
        return

    balances[user_id] = 100000

    await interaction.response.send_message(
        "10만원 지급 완료!"
    )

# ===== 돈 확인 =====

@bot.tree.command(name="돈", description="잔액 확인")
async def check_money(interaction: discord.Interaction):

    money = balances.get(interaction.user.id, 0)

    await interaction.response.send_message(
        f"현재 잔액: {money:,}원"
    )

# ===== 돈 지급 =====

@bot.tree.command(name="돈지급", description="관리자 전용 돈 지급")
@app_commands.describe(
    유저="지급할 대상",
    금액="지급 금액"
)
async def give_money(
    interaction: discord.Interaction,
    유저: discord.User,
    금액: int
):

    if not is_admin(interaction.user.id):
        await interaction.response.send_message(
            "관리자 전용 명령어입니다.",
            ephemeral=True
        )
        return

    if 금액 <= 0:
        await interaction.response.send_message(
            "금액은 1 이상이어야 합니다.",
            ephemeral=True
        )
        return

    balances[유저.id] = balances.get(유저.id, 0) + 금액

    await interaction.response.send_message(
        f"{유저.name} 님에게 {금액:,}원 지급 완료!"
    )

# ===== 도박 =====

@bot.tree.command(name="도박", description="도박 게임")
@app_commands.describe(금액="도박할 금액")
async def gamble(
    interaction: discord.Interaction,
    금액: int
):

    user_id = interaction.user.id

    balance = balances.get(user_id, 0)

    if 금액 <= 0:
        await interaction.response.send_message(
            "1원 이상 입력하세요.",
            ephemeral=True
        )
        return

    if balance < 금액:
        await interaction.response.send_message(
            "잔액 부족!",
            ephemeral=True
        )
        return

    # 잭팟 1%
    jackpot = random.randint(1, 100)

    if jackpot == 1:

        reward = 금액 * 5

        balances[user_id] += reward

        await interaction.response.send_message(
            f"🎉 JACKPOT!!!\n{reward:,}원 획득!"
        )

        return

    # 일반 확률
    result = random.choice(["win", "lose"])

    if result == "win":

        balances[user_id] += 금액

        await interaction.response.send_message(
            f"승리!\n{금액:,}원 획득!"
        )

    else:

        balances[user_id] -= 금액

        await interaction.response.send_message(
            f"패배...\n{금액:,}원 잃음!"
        )

# ===== 업다운 시작 =====

@bot.tree.command(name="업다운", description="업다운 게임 시작")
async def updown(interaction: discord.Interaction):

    number = random.randint(1, 100)

    games[interaction.user.id] = number

    await interaction.response.send_message(
        "업다운 게임 시작!\n/숫자 입력:50 형태로 입력하세요!"
    )

# ===== 숫자 입력 =====

@bot.tree.command(name="숫자", description="숫자 입력")
@app_commands.describe(입력="숫자 입력")
async def number_guess(
    interaction: discord.Interaction,
    입력: int
):

    user_id = interaction.user.id

    if user_id not in games:
        await interaction.response.send_message(
            "먼저 /업다운 을 입력하세요.",
            ephemeral=True
        )
        return

    answer = games[user_id]

    if 입력 < answer:

        await interaction.response.send_message("업!")

    elif 입력 > answer:

        await interaction.response.send_message("다운!")

    else:

        del games[user_id]

        await interaction.response.send_message(
            "정답!!!"
        )

# ===== 실행 =====

bot.run(TOKEN)