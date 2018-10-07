import os
from time import time

from flask import Flask, render_template, jsonify, request, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Message is a tuple:
# (timestamp, username, body)
#   - timestamp is Float; interp. as seconds since epoch
#   - username is String
#   - body is String
messages = [
  (1234, "Server", "Test message 1."),
  (1235, "Server", "Test message 2."),
  (2345, "Neo", "Meow Meow")
]

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

@app.route("/fetchMessages", methods=['GET'])
def getMessages():
  # Initialize useful variables
  arrMessages = []

  # Iterate over each Message tuple in the list of messages
  for message in messages:
    arrMessages.append(messageToDict(message))
  
  jsonResponse = jsonify(success=True, messages=arrMessages)
  return jsonResponse

@socketio.on("login")
def login(data):
  # call handle_receive_message using login info
  _username = data['username']
  _body = f"User {_username} logged in to chat"
  handle_receive_message({'username': _username, 'body': _body})
  print(f"User {data['username']} logged in to chat")

@socketio.on("clientMessage")
def handle_receive_message(data):
  # create new Message object
  newMessage = (time(), data['username'], data['body'])
  print(f"Received new message: {str(newMessage)}")

  # add it to the list of messages
  messages.append(newMessage)

  # rebroadcast message to clients
  socketio.emit('serverMessage', messageToDict(newMessage))


### Helpers

def messageToDict(message):
  messageDict = {}
  messageDict['timestamp'] = message[0]
  messageDict['username'] = message[1]
  messageDict['body'] = message[2]
  return messageDict