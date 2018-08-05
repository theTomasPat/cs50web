import os

from flask import Flask, session, request, redirect, escape, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
  raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
  if 'username' in session:
    return "Logged in as {}".format(escape(session['username']))
  return "You are not logged in."

@app.route("/login", methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    session['username'] = request.form['username']
    return redirect(url_for('index'))
  return '''
    <form method="post">
      <input type="text" name="username">
      <button>Login</button>
    </form>
    '''

@app.route("/logout")
def logout():
  session.pop('username', None)
  return redirect(url_for('index'))
