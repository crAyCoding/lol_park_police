import sqlite3

# 데이터베이스 파일 저장소
warnings_db = '/database/warnings.db'

# 소환사 등록
def add_summoner(member):
    conn = sqlite3.connect(warnings_db)
    db = conn.cursor()
    try:
        # 해당 id가 존재하는지 확인
        db.execute('SELECT id FROM summoners WHERE id = ?', (member.id,))
        result = db.fetchone()

        # id가 존재하지 않으면 삽입
        if result is None:
            db.execute('''
            INSERT INTO summoners (id, display_name, server_warning, game_warning) 
            VALUES (?, ?, ?, ?)
            ''',
                       (member.id, member.display_name, 0, 0))
            conn.commit()
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()
        conn.close()


# 테이블 생성, db 파일 바꾸고 1회만 진행
def create_table():
    conn = sqlite3.connect(warnings_db)
    db = conn.cursor()
    # summoners 테이블 생성
    db.execute('''
    CREATE TABLE IF NOT EXISTS summoners (
        id INTEGER NOT NULL,
        display_name TEXT NOT NULL,
        server_warning INTEGER NOT NULL,
        game_warning INTEGER NOT NULL
    )
    ''')
    conn.commit()
    db.close()
    conn.close()


# 서버 경고 1회 추가
async def add_server_warning(member):
    conn = sqlite3.connect(warnings_db)
    db = conn.cursor()
    try:
        # server_warning 값을 1 증가
        query = 'UPDATE summoners SET server_warning = server_warning + 1 WHERE id = ?'
        db.execute(query, (member.id,))
        conn.commit()

        # 업데이트된 server_warning 값을 조회
        db.execute('SELECT server_warning FROM summoners WHERE id = ?', (member.id,))
        result = db.fetchone()
        
        if result:
            return int(result[0])  # server_warning 값을 반환
        else:
            return None

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        db.close()
        conn.close()


# 내전 경고 1회 추가
async def add_game_warning(member):
    conn = sqlite3.connect(warnings_db)
    db = conn.cursor()
    try:
        query = f'UPDATE summoners SET game_warning = game_warning + 1 WHERE id = ?'
        # 쿼리 실행
        db.execute(query, (member.id,))
        # 변경사항 저장
        conn.commit()

        # 업데이트된 game_warning 값을 조회
        db.execute('SELECT game_warning FROM summoners WHERE id = ?', (member.id,))
        result = db.fetchone()
        
        if result:
            return int(result[0])  # game_warning 값을 반환
        else:
            return None
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()
        conn.close()