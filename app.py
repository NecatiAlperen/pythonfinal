from flask import Flask, render_template, request, url_for, flash, redirect, session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config["SECRET_KEY"] = "jRv8sL2pFwXhN5aG9zQ3bU7cY6dA1eR4"


def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_connection()
    post = conn.execute(
        """
        SELECT posts.*, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.id = ?
    """,
        (post_id,),
    ).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route("/")
def index():
    conn = get_connection()
    posts = conn.execute('''
        SELECT posts.*, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
    ''').fetchall()
    conn.close()
    return render_template("index.html", posts=posts)   


@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    return render_template("post.html", post=post)


@app.route("/create", methods=["GET", "POST"])
def create():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if not title:
            flash("Title is required!")
        else:
            conn = get_connection()
            conn.execute(
                "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
                (session["user_id"], title, content),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
    return render_template("create.html")


@app.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    post = get_post(id)
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if not title:
            flash("Title is required!")
        else:
            conn = get_connection()
            conn.execute(
                "UPDATE posts SET title = ?, content = ? WHERE id = ?",
                (title, content, id),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
    return render_template("edit.html", post=post)


@app.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    post = get_post(id)
    conn = get_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash(' "{}" was successfully deleted!'.format(post["title"]))
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password),
        )
        conn.commit()
        conn.close()
        flash("Registration successful! Please login.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid email or password")
        else:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            if user["username"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    if session.get("username") != "admin":
        return redirect(url_for("index"))

    conn = get_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return render_template("admin.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
