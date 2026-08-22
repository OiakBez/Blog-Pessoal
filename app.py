from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/post/<int:id>")
def post(id):
    return render_template("post.html")

if __name__ == "__main__":
    app.run(debug=True)