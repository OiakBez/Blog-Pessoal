from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Meu primeiro blog!"

if __name__ == "__main__":
    app.run(debug=True)