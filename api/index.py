from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1 style='color:white;background:black;text-align:center;padding:50px;'>Zenith Guard is Online!</h1>"
