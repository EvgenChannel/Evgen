import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="postgres", user="postgres", password="postgres", host="db", port="5432"
)
cursor = conn.cursor()

# Функция для создания таблиц, если их нет
def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
            sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()

# Вызываем создание таблиц при старте
create_tables()

# Получение пользователя по имени
def get_user_by_username(username):
    cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
    return cursor.fetchone()

# Создание нового пользователя
def create_user(username):
    cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (username,))
    conn.commit()
    return cursor.fetchone()[0]

# Получение чата по имени
def get_chat_by_name(name):
    cursor.execute("SELECT * FROM chats WHERE name = %s;", (name,))
    return cursor.fetchone()

# Создание нового чата
def create_chat(name):
    cursor.execute("INSERT INTO chats (name) VALUES (%s) RETURNING id;", (name,))
    conn.commit()
    return cursor.fetchone()[0]

# Сохранение сообщения в чат
def save_message(chat_id, sender_id, content):
    cursor.execute("INSERT INTO messages (chat_id, sender_id, content) VALUES (%s, %s, %s);",
                   (chat_id, sender_id, content))
    conn.commit()

# Получение всех сообщений для чата
def get_messages_for_chat(chat_id):
    cursor.execute("SELECT m.content, m.timestamp, u.username FROM messages m "
                   "JOIN users u ON m.sender_id = u.id WHERE m.chat_id = %s ORDER BY m.timestamp;",
                   (chat_id,))
    return cursor.fetchall()
