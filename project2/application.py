import os

from flask import Flask, render_template, jsonify, request, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fetchHTML/<string:resource>", methods=['GET'])
def fetchHTML(resource):
    try:
        htmlFile = open(f'static/clientTemplates/{resource}.html', 'rt')
        loginHtml = htmlFile.read()
        print(f'Received request for {resource} page, sending response now')
    except:
        print(f'Request for {resource} not found, sending response now')
        return jsonify({"success": False})

    return jsonify({"success": True, "data": loginHtml})
