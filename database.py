import sqlite3


class GameDatabase:
    """Менеджер игровых сессий"""

    def __init__(self, db_name='game.db'):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных - создание таблицы если её нет"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_session (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            level_completed INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    def save_level(self, level_completed):
        """Сохраняет пройденный уровень в базу"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO game_session (level_completed) VALUES (?)",
            (level_completed,)
        )

        conn.commit()
        conn.close()
