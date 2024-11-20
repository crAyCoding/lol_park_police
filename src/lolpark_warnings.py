import database

async def server_warning(ctx, member):
    # id로 db에 등록 (db에 id가 없는 경우)
    database.add_summoner(member)
    # 서버경고 1회 추가
    number_of_warnings = await database.add_server_warning(member)
    return number_of_warnings


async def game_warning(ctx, member):
    # id로 db에 등록 (db에 id가 없는 경우)
    database.add_summoner(member)
    # 게임경고 1회 추가
    number_of_warnings = await database.add_game_warning(member)
    return number_of_warnings