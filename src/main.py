import os
import discord
from discord.ext import commands
from bot import bot
from dotenv import load_dotenv
from lolpark_warnings import server_warning, game_warning, remove_server_warning, remove_game_warning
import database
import asyncio
import channels
from functions import get_nickname_from_display_name


# 테스트 할때 아래 사용
load_dotenv()
# GitHub Secrets에서 가져오는 값
TOKEN = os.getenv('DISCORD_TOKEN')


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {synced} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")


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


@bot.command(name='경고검색')
async def find_warning(ctx):
    guild = ctx.guild
    game_1 = discord.utils.get(guild.roles, name='game 1')
    game_2 = discord.utils.get(guild.roles, name='game 2')
    game_3 = discord.utils.get(guild.roles, name='game 3')
    game_4 = discord.utils.get(guild.roles, name='game 4')
    server_1 = discord.utils.get(guild.roles, name='server 1')
    server_2 = discord.utils.get(guild.roles, name='server 2')

    members_with_game_1 = [member for member in guild.members if game_1 in member.roles]

    if not members_with_game_1:
        await ctx.send(f"'{game_1}' 역할을 가진 멤버가 없습니다.")
    else:
        
        # 멤버 이름 출력
        member_names = "\n".join(get_nickname_from_display_name(member.display_name) for member in members_with_game_1)
        await ctx.send(f"게임경고 1회 이상 부여받은 멤버 목록입니다.\n{member_names}")


class WarningModal(discord.ui.Modal):
    def __init__(self, user):
        super().__init__(title="유저 메시지 작성")
        self.user = user

        # 메시지 입력 필드
        self.message = discord.ui.TextInput(label="메시지", placeholder="유저에게 보낼 메시지를 입력하세요...")
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        # 메시지 제출 시 실행
        await interaction.response.send_message(
            f"**닉네임:** {self.user.display_name}\n**메시지:** {self.message.value}",
            ephemeral=True
        )


# 자동완성 핸들러
@bot.tree.command(name="경고", description="유저 닉네임을 검색하고 경고를 부여하세요.")
@discord.app_commands.describe(query="검색할 닉네임의 일부를 입력하세요")
async def user_search(interaction: discord.Interaction, query: str):

    guild = interaction.guild
    user = discord.utils.find(lambda m: query.lower() in m.display_name.lower(), guild.members)

    if user is None:
        await interaction.response.send_message(f"'{query}'에 해당하는 사용자를 찾을 수 없습니다.", ephemeral=True)
    else:
        # Modal 열기
        modal = WarningModal(user)
        await interaction.response.send_modal(modal)



# 자동완성 함수
@user_search.autocomplete("query")
async def user_search_autocomplete(interaction: discord.Interaction, current: str):
    guild = interaction.guild
    if not guild:
        return []
    
    # 현재 입력된 내용(current)을 포함하는 멤버 닉네임 리스트 생성
    matches = [
        discord.app_commands.Choice(name=member.display_name, value=member.display_name)
        for member in guild.members
        if current.lower() in member.display_name.lower()
    ]

    # 최대 25개의 결과만 반환 (Discord 제한)
    return matches[:25]


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
