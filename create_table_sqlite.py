import sqlite3

# SQL скрипт (адаптированный для SQLite)
SQL_SCRIPT = """
CREATE TABLE IF NOT EXISTS game_session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    level_completed INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_game_session_player_id ON game_session(player_id);
CREATE INDEX IF NOT EXISTS idx_game_session_created_at ON game_session(created_at);
"""


def main():
    try:
        # Подключаемся к базе (файл создастся автоматически)
        conn = sqlite3.connect('game_database.db')
        cursor = conn.cursor()

        # Выполняем SQL скрипт
        cursor.executescript(SQL_SCRIPT)
        conn.commit()

        print("✅ Таблица 'game_session' успешно создана в SQLite!")
        print(f"📁 Файл базы: game_database.db")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()