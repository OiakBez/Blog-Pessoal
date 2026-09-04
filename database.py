from werkzeug.security import generate_password_hash
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("blog.db")
    conn.row_factory = sqlite3.Row

    return conn

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def create_admin():
    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if user is None:
        password_hash = generate_password_hash("1234")
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", password_hash)
        )

        conn.commit()

    conn.close()

def get_all_posts():
    conn = get_db_connection()

    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    conn.close()
    return posts

def get_post(post_id):
    conn = get_db_connection()

    post = conn.execute(
        "SELECT * FROM posts WHERE id = ?",
        (post_id,)
    ).fetchone()

    conn.close()

    return post

def add_post(title, content):
    conn = get_db_connection()

    cursor = conn.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()
    conn.close()

def update_post(post_id, title, content):
    conn = get_db_connection()

    conn.execute(
        "UPDATE posts SET title = ?, content = ? WHERE id = ?",
        (title, content, post_id)
    )

    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM posts WHERE id = ?",
        (post_id,)
    )

    conn.commit()
    conn.close()