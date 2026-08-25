from flask import Flask, render_template, abort, request, redirect, url_for
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
    cursor = conn.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()

    post_id = cursor.lastrowid

    conn.close()

    return post_id

@app.route("/")
def home():
    conn = get_db_connection()
    
    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template("index.html", posts=posts)

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

        post_id = add_post(title, content)

        return redirect(url_for("post", id=post_id))

    return render_template("create_post.html")

@app.route("/edit-post/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    conn = get_db_connection()
    post = conn.execute(
        "SELECT * FROM posts WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if post is None:
        abort (404)

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        conn = get_db_connection()

        conn.execute(
            """
            UPDATE posts
            SET title = ?, content = ?
            WHERE id = ?
            """,
            (title, content, id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("post", id=id))
    return render_template("edit_post.html", post=post)

@app.route("/delete-post/<int:id>", methods=["POST"])
def delete_post(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM posts WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(debug=False)