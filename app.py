from flask import Flask, render_template, abort, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import check_password_hash
from database import get_db_connection, init_db, create_admin

app = Flask(__name__)

app.secret_key = "&@?SPbLwwrr])+WT"

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

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():

    if "user_id" not in session:
        return None

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    conn.close()

    return user

@app.context_processor
def inject_user():

    return {
        "user": get_current_user()
    }

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
@login_required
def create_post():

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        post_id = add_post(title, content)

        return redirect(url_for("post", id=post_id))

    return render_template("create_post.html")

@app.route("/edit-post/<int:id>", methods=["GET", "POST"])
@login_required
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
@login_required
def delete_post(id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM posts WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user is not None and check_password_hash(user["password"], password):
            
            session["user_id"] = user["id"]

            flash("Login realizado com sucesso. Bem vindo!", "success")

            return redirect(url_for("home"))

        flash("Usuário ou senha incorretos.", "error")
        return redirect(url_for("login")) 
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()

    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    create_admin()
    app.run(debug=False)