import os
import discord
from discord.ext import commands
from bot import bot
from dotenv import load_dotenv
from lolpark_warnings import server_warning, game_warning, remove_server_warning, remove_game_warning
import database
import asyncio
import channels

# 테스트 할때 아래 사용
load_dotenv()
# GitHub Secrets에서 가져오는 값
TOKEN = os.getenv('DISCORD_TOKEN')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command(name='서버경고')
@commands.has_role("관리자")
@commands.has_permissions(manage_roles=True)
async def command_server_warning(ctx, member: discord.Member = None):
    await ctx.message.delete()

    # 언급 멤버가 없으면 무시
    if not member:
        return
    
    # 정해진 채팅 채널이 아닌 경우 무시
    channel_id = ctx.channel.id
    if channel_id != channels.PUNISHMENT_CHANNEL_ID and channel_id != channels.TEST_ID:
        return
    
    num_of_warnings = await server_warning(ctx, member)
    if num_of_warnings == 3:
        await ctx.send(f"{member.mention}님에게 서버 경고가 부여되었습니다.\n"
                       f"누적 서버 경고 : {num_of_warnings}회\n"
                       f"처분 : 서버 추방 및 재입장 불가")
        return

    role = discord.utils.get(ctx.guild.roles, name=f'server {num_of_warnings}')
    # 내전경고 횟수에 따른 처분 목록
    punishment = f'타임아웃 7일'
    
    if num_of_warnings == 2:
        punishment = f'타임아웃 14일'

    try:
        # 역할 부여
        await member.add_roles(role)
        await ctx.send(f"{member.mention}님에게 서버 경고가 부여되었습니다.\n"
                       f"누적 서버 경고 : {num_of_warnings}회\n"
                       f"처분 : {punishment}")
    except Exception as e:
        print('오류 발생')
    return


@bot.command(name='게임경고')
@commands.has_role("관리자")
@commands.has_permissions(manage_roles=True)
async def command_game_warning(ctx, member: discord.Member = None):
    await ctx.message.delete()

    # 언급 멤버가 없으면 무시
    if not member:
        return
    
    # 정해진 채팅 채널이 아닌 경우 무시
    channel_id = ctx.channel.id
    if channel_id != channels.PUNISHMENT_CHANNEL_ID and channel_id != channels.TEST_ID:
        return
    
    num_of_warnings = await game_warning(ctx, member)

    # num_of_warnings = 1

    if num_of_warnings == 5:
        await ctx.send(f"{member.mention}님에게 게임 경고가 부여되었습니다.\n"
                       f"누적 게임 경고 : {num_of_warnings}회\n"
                       f"처분 : 서버 추방 및 재입장 불가")
        return

    role = discord.utils.get(ctx.guild.roles, name=f'game {num_of_warnings}')
    game_ban_role = discord.utils.get(ctx.guild.roles, name=f'내전금지')
    # 게임경고 횟수에 따른 처분 목록
    punishment = f'내전 참여금지 1일'
    
    if num_of_warnings == 2:
        punishment = f'내전 참여금지 3일, 타임아웃 1일'
    if num_of_warnings == 3:
        punishment = f'타임아웃 7일'
    if num_of_warnings == 4:
        punishment = f'타임아웃 14일'

    try:
        # 역할 부여
        await member.add_roles(role)
        await ctx.send(f"{member.mention}님에게 게임 경고가 부여되었습니다.\n"
                       f"누적 게임 경고 : {num_of_warnings}회\n"
                       f"처분 : {punishment}")
        if num_of_warnings <= 2:
            await member.add_roles(game_ban_role)
            await asyncio.sleep(86400 + (num_of_warnings - 1) * 86400 * 2)
            await member.remove_roles(game_ban_role)

    except Exception as e:
        print(f'오류 발생 : {e}')
    return


@bot.command(name='서버경고철회')
@commands.has_role("관리자")
@commands.has_permissions(manage_roles=True)
async def command_server_warning(ctx, member: discord.Member = None):
    await ctx.message.delete()

    # 언급 멤버가 없으면 무시
    if not member:
        return
    
    # 정해진 채팅 채널이 아닌 경우 무시
    channel_id = ctx.channel.id
    if channel_id != channels.PUNISHMENT_CHANNEL_ID and channel_id != channels.TEST_ID:
        return
    
    num_of_warnings = await remove_server_warning(ctx, member)

    if not num_of_warnings:
        return

    try:
        await ctx.send(f"{member.mention}님의 서버 경고를 철회했습니다.\n"
                       f"누적 서버 경고 : {num_of_warnings}회\n")
    except Exception as e:
        print('오류 발생')
    return


@bot.command(name='게임경고철회')
@commands.has_role("관리자")
@commands.has_permissions(manage_roles=True)
async def command_server_warning(ctx, member: discord.Member = None):
    await ctx.message.delete()

    # 언급 멤버가 없으면 무시
    if not member:
        return
    
    # 정해진 채팅 채널이 아닌 경우 무시
    channel_id = ctx.channel.id
    if channel_id != channels.PUNISHMENT_CHANNEL_ID and channel_id != channels.TEST_ID:
        return
    
    num_of_warnings = await remove_game_warning(ctx, member)
    
    if not num_of_warnings:
        return

    try:
        await ctx.send(f"{member.mention}님의 게임 경고를 철회했습니다.\n"
                       f"누적 게임 경고 : {num_of_warnings}회\n")
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


# 명령어 에러 처리
@bot.event
async def on_command_error(ctx, error):
    # CommandNotFound 에러는 무시
    if isinstance(error, commands.CommandNotFound):
        pass  # 아무 작업도 하지 않음
    else:
        # 다른 에러는 콘솔에 출력
        print(f"Unhandled error: {error}")


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


@bot.command(name='테스트')
@commands.is_owner()
async def test_command(ctx):
    print(database.is_more_than_three_game(ctx))


def main() -> None:
    # database.create_table()
    bot.run(token=TOKEN)


if __name__ == '__main__':
    main()
