import sqlite3

# Path to your SQLite database file
DB_PATH = 'chat_app.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete all users (and optionally all conversations/messages)
cursor.execute('DELETE FROM users')
cursor.execute('DELETE FROM conversations')
cursor.execute('DELETE FROM messages')
cursor.execute('DELETE FROM documents')
conn.commit()
print('All users, conversations, messages, and documents deleted.')
conn.close()
