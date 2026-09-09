import os
import math
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, abort, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from werkzeug.security import check_password_hash
from database import (
    get_db_connection,
    init_db,
    create_admin,
    get_all_posts,
    search_posts,
    get_posts_count,
    get_post,
    add_post,
    update_post,
    delete_post as delete_post_db,
    get_user_by_id,
    get_user_by_username
)

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY')

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

    return get_user_by_id(session["user_id"])

@app.context_processor
def inject_user():

    return {
        "user": get_current_user()
    }

@app.template_filter("format_datetime")
def format_datetime(value):
    if not value:
        return ""

    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(ZoneInfo("America/Recife"))

    return dt.strftime("%d/%m/%Y às %H:%M")

@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)

    posts_per_page = 5
    offset = (page - 1) * posts_per_page

    posts = get_all_posts(posts_per_page, offset)

    total_posts = get_posts_count()
    total_pages = math.ceil(total_posts/posts_per_page)

    return render_template("index.html", posts=posts, page=page, total_pages=total_pages)

@app.route("/post/<int:id>")
def post(id):
    post = get_post(id)

    if post is None:
        return "Post não encontrado.", 404

    return render_template("post.html", post=post)

@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title or not content:
            flash("Título e conteúdo são obrigatórios.", "error")
            return redirect(request.referrer or url_for("home"))

        post_id = add_post(title, content)

        return redirect(url_for("post", id=post_id))

    return render_template("create_post.html")

@app.route("/edit-post/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = get_post(id)

    if post is None:
        return "Post não encontrado.", 404

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title or not content:
            flash("Título e conteúdo são obrigatórios.", "error")
            return redirect(request.referrer or url_for("home"))

        update_post(id, title, content)

        return redirect(url_for("post", id=id))
    return render_template("edit_post.html", post=post)

@app.route("/delete-post/<int:id>", methods=["POST"])
@login_required
def delete_post(id):
    delete_post_db(id)

    return redirect(url_for("home"))

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    posts = []

    if query:
        posts = search_posts(query)

    return render_template("index.html", posts=posts,page=1, total_pages=1, search_query=query)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        
        user = get_user_by_username(username)

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

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    init_db()
    create_admin()
    app.run(debug=False)