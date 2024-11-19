import os
import discord
from discord.ext import commands
from bot import bot
from dotenv import load_dotenv
from lolpark_warnings import server_warning, game_warning
import database

# 테스트 할때 아래 사용
load_dotenv()
# GitHub Secrets에서 가져오는 값
TOKEN = os.getenv('DISCORD_TOKEN')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command(name='서버경고')
@commands.has_permissions(manage_roles=True)
async def command_server_warning(ctx, member: discord.Member = None):
    await ctx.message.delete()
    if not member:
        return
    num_of_warnings = await server_warning(ctx, member)
    role = discord.utils.get(ctx.guild.roles, name=f'server {num_of_warnings}')
    try:
        # 역할 부여
        await member.add_roles(role)
        await ctx.send(f"{member.mention}님에게 서버 경고가 부여되었습니다.\n"
                       f"누적 서버 경고 : {num_of_warnings}회")
    except Exception as e:
        print('오류 발생')
    return


@bot.command(name='내전경고')
@commands.has_permissions(manage_roles=True)
async def command_game_warning(ctx, member: discord.Member = None):
    await ctx.message.delete()
    if not member:
        return
    num_of_warnings = await game_warning(ctx, member)
    role = discord.utils.get(ctx.guild.roles, name=f'game {num_of_warnings}')
    try:
        # 역할 부여
        await member.add_roles(role)
        await ctx.send(f"{member.mention}님에게 내전 경고가 부여되었습니다.\n"
                       f"누적 내전 경고 : {num_of_warnings}회")
    except Exception as e:
        print('오류 발생')
    return


# 메세지 입력 시 마다 수행
@bot.event
async def on_message(message):

    # 봇 메세지는 메세지로 인식 X
    if message.author == bot.user:
        return

    await bot.process_commands(message)


# 메세지 삭제 시 마다 수행
@bot.event
async def on_message_delete(message):

    # 봇 메세지는 메세지로 인식 X
    if message.author == bot.user:
        return


# 서버원 상태 바뀔 때 마다 수행
@bot.event
async def on_member_update(before, after):
    return


@bot.command(name='퇴근')
@commands.is_owner()
async def shutdown(ctx):
    # 디스코드에서 봇 종료를 위한 명령어
    await ctx.send("롤파크 경찰관 퇴근합니다.")
    await bot.close()


def main() -> None:
    database.create_table()
    bot.run(token=TOKEN)


if __name__ == '__main__':
    main()
