from flask import Flask, render_template, abort, request
import sqlite3

app = Flask(__name__)

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

    conn.commit()
    conn.close()


def add_post(title, content):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/post/<int:id>")
def post(id):
    conn = get_db_connection()

    post = conn.execute(
        "SELECT * FROM posts WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if post is None:
        abort(404)

    return render_template("post.html", post=post)

@app.route("/create-post", methods=["GET", "POST"])
def create_post():

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        add_post(title, content)

        return "Post criado com sucesso."

    return render_template("create_post.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=False)