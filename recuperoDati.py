import sqlite3

db_filename = 'todo.db'

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()

    cursor.execute("""
    select Server, Username, Password ,ChatIdTelegram, BotTelegram, LastUpdateId, PlayerId from UserConfiguration
    """)

    for row in cursor.fetchall():
        Server, Username, Password, ChatIdTelegram, BotTelegram, LastUpdateId, PlayerId = row
        print '%s %s %s %s %s %s %s' % (Server, Username, Password, ChatIdTelegram, BotTelegram, LastUpdateId, PlayerId)