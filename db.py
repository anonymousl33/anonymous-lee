import sqlite3
from datetime import datetime
import pytz

DB_NAME = "messages.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ensure base table exists first (without new cols)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            message TEXT,
            sender TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')

    # Add new columns if missing
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN type TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN artist TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN song TEXT")
    except sqlite3.OperationalError:
        pass

    # Wall posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wall_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            message TEXT,
            sender TEXT,
            status TEXT,
            timestamp TEXT,
            admin_reply TEXT,
            wall_timestamp TEXT
        )
    ''')

    # Public posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS public_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp TEXT,
            image TEXT,
            attachment TEXT
        )
    ''')

    conn.commit()
    conn.close()

def save_message(message_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (recipient, message, sender, status, timestamp, type, artist, song)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        message_data.get("recipient"),
        message_data.get("message"),
        message_data.get("from", "Anonymous"),
        message_data.get("status", "new"),
        message_data.get("timestamp", datetime.now(pytz.timezone("Asia/Manila")).strftime("%Y-%m-%d %I:%M %p")),
        message_data.get("type"),
        message_data.get("artist"),
        message_data.get("song")
    ))
    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT recipient, message, sender, status, timestamp, type, artist, song FROM messages')
    rows = cursor.fetchall()
    conn.close()

    messages = []
    for row in rows:
        messages.append({
            "recipient": row[0],
            "message": row[1],
            "from": row[2],
            "status": row[3],
            "timestamp": row[4],
            "type": row[5],
            "artist": row[6],
            "song": row[7]
        })
    return messages

def save_wall_post(post_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO wall_posts (recipient, message, sender, status, timestamp, admin_reply, wall_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        post_data.get("recipient"),
        post_data.get("message"),
        post_data.get("from", "Anonymous"),
        post_data.get("status", "seen"),
        post_data.get("timestamp"),
        post_data.get("admin_reply"),
        post_data.get("wall_timestamp")
    ))
    conn.commit()
    conn.close()

def load_wall_posts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, recipient, message, sender, status, timestamp, admin_reply, wall_timestamp
        FROM wall_posts
    ''')
    rows = cursor.fetchall()
    conn.close()

    posts = []
    for row in rows:
        posts.append({
            "id": row[0],
            "recipient": row[1],
            "message": row[2],
            "from": row[3],
            "status": row[4],
            "timestamp": row[5],
            "admin_reply": row[6],
            "wall_timestamp": row[7],
        })
    return posts

def save_wall_posts(all_posts):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Delete all existing wall posts first
    cursor.execute("DELETE FROM wall_posts")

    # Re-insert all posts
    for post in all_posts:
        cursor.execute('''
            INSERT INTO wall_posts (recipient, message, sender, status, timestamp, admin_reply, wall_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.get("recipient"),
            post.get("message"),
            post.get("from", "Anonymous"),
            post.get("status", "seen"),
            post.get("timestamp"),
            post.get("admin_reply"),
            post.get("wall_timestamp")
        ))

    conn.commit()
    conn.close()

def save_public_post(post_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO public_posts (content, timestamp, image, attachment)
        VALUES (?, ?, ?, ?)
    ''', (
        post_data.get("content"),
        post_data.get("timestamp"),
        post_data.get("image"),
        post_data.get("attachment")
    ))
    conn.commit()
    conn.close()

def load_public_posts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT content, timestamp, image, attachment
        FROM public_posts
    ''')
    rows = cursor.fetchall()
    conn.close()

    posts = []
    for row in rows:
        posts.append({
            "content": row[0],
            "timestamp": row[1],
            "image": row[2],
            "attachment": row[3],
        })
    return posts

def save_public_posts(all_posts):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Delete all existing public posts first
    cursor.execute("DELETE FROM public_posts")

    # Re-insert all posts
    for post in all_posts:
        cursor.execute('''
            INSERT INTO public_posts (content, timestamp, image, attachment)
            VALUES (?, ?, ?, ?)
        ''', (
            post.get("content"),
            post.get("timestamp"),
            post.get("image"),
            post.get("attachment")
        ))

    conn.commit()
    conn.close()

def save_messages(all_messages):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Delete everything first
    cursor.execute("DELETE FROM messages")

    # Re-insert all messages
    for msg in all_messages:
        cursor.execute('''
            INSERT INTO messages (recipient, message, sender, status, timestamp, type, artist, song)
	    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	''', (
	    msg.get("recipient"),
    	    msg.get("message"),
    	    msg.get("from", "Anonymous"),
    	    msg.get("status", "new"),
    	    msg.get("timestamp"),   # <--- still saving date/time here
    	    msg.get("type"),
    	    msg.get("artist"),
    	    msg.get("song")
	))

    conn.commit()
    conn.close()

def delete_wall_post_by_id(post_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wall_posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def update_message_status_by_index(index, new_status):
    messages = load_messages()
    actual_index = len(messages) - 1 - index
    if 0 <= actual_index < len(messages):
        messages[actual_index]['status'] = new_status
        save_messages(messages)

def delete_message_by_index(index):
    messages = load_messages()
    actual_index = len(messages) - 1 - index
    if 0 <= actual_index < len(messages):
        messages.pop(actual_index)
        save_messages(messages)

def mark_message_as_seen(index):
    messages = load_messages()
    actual_index = len(messages) - 1 - index
    if 0 <= actual_index < len(messages):
        messages[actual_index]['status'] = 'seen'
        save_messages(messages)

def update_message_table_for_music():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN type TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN artist TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN song TEXT")
    except:
        pass
    conn.commit()
    conn.close()