import os
from time import time

from flask import Flask, render_template, jsonify, request, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

messagesMaxLen = 100

# Message is a tuple:
# (timestamp, username, body)
#   - timestamp is Float; interp. as seconds since epoch
#   - username is String
#   - body is String
lobbyMessages = [
  (1234, "Server", "Test message 1."),
  (1235, "Server", "Test message 2."),
  (2345, "Neo", "Meow Meow")
]

room1Messages = [
  (3456, "Server-Room1", "Hello from Room1"),
  (3578, "Server-Room1", "Another greeting from Room1"),
  (3689, "Server-Room1", "Last hello from Room1")
]

# chatRooms is a Dict
# key: names of the rooms
# value: list of Message
chatRooms = {
  'Lobby': lobbyMessages,
  'Room1': room1Messages
}

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

@app.route("/fetchMessages/<string:room>", methods=['GET'])
def getMessages(room):
  # Initialize useful variables
  arrMessages = []

  # Iterate over each Message tuple in the list of messages
  for message in chatRooms[room]:
    arrMessages.append(messageToDict(message))
  
  jsonResponse = jsonify(success=True, messages=arrMessages)
  return jsonResponse

@app.route("/fetchRooms", methods=['GET'])
def getRooms():
  # initialize useful vars
  arrRooms = []

  # iterate over the list of rooms
  for room in chatRooms:
    arrRooms.append(room)

  # generate a JSON object using the list of rooms and return that
  jsonResponse = jsonify(success=True, rooms=arrRooms)
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

  chatRoom = data['room']
  # add incoming message to the list of messages
  chatRooms[chatRoom].append(newMessage)
  chatRooms[chatRoom] = limitListLength(chatRooms[chatRoom], messagesMaxLen)

  print(f'Added new message to room {chatRoom}: {newMessage}')

  # rebroadcast message to client's room
  socketio.emit('serverMessage', messageToDict(newMessage), room=chatRoom)

@socketio.on("joinRoom")
def handle_join_room(data):
  leave_room(data['currentRoom'])
  join_room(data['desiredRoom'])
  print(f"Someone just joined {data['desiredRoom']}")

  # if that chat room doesn't already exist, add it to the list of rooms
  if not data['desiredRoom'] in chatRooms:
    chatRooms[data['desiredRoom']] = []

### Helpers

def messageToDict(message):
  """Return a Dict object made from the properties of message"""
  messageDict = {}
  messageDict['timestamp'] = message[0]
  messageDict['username'] = message[1]
  messageDict['body'] = message[2]
  return messageDict

def limitListLength(list, maxLen):
  """Return a list with maxLen number of elements"""
  if len(list) > maxLen:
    return list[:maxLen]
  
  return list