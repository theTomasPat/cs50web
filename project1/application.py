import os

from flask import Flask, session, request, redirect, escape, url_for, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from src.dbRunner import addUser

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

''' APP ROUTES '''
@app.route("/")
def index():
  # Dummy data vv
  bookList = [
    {
      'name': 'Top 40',
      'books': [
        {
          'isbn': '123',
          'coverImage': 'http://cataas.com/cat?width=200',
          'title': 'Random Book Title',
          'author': "Random Author",
          'description': 'Lorem dolor sit amet'
        },
        {
          'isbn': '456',
          'coverImage': 'http://thecatapi.com/api/images/get?format=src&type=gif',
          'title': 'Random Book Title 2',
          'author': "Random Author 2",
          'description': 'Lorem dolor sit amet 2'
        }
      ]
    },
    {
      'name': 'Random',
      'books': [
        {
          'isbn': '789',
          'coverImage': 'http://cataas.com/cat?width=200',
          'title': 'Random Book Title 3',
          'author': "Random Author 3",
          'description': 'Lorem dolor sit amet 3'
        },
        {
          'isbn': '1337',
          'coverImage': 'http://thecatapi.com/api/images/get?format=src&type=gif',
          'title': 'Random Book Title 4',
          'author': "Random Author 4",
          'description': 'Lorem dolor sit amet 4'
        }
      ]
    }
  ]

  if 'username' in session:
    #return "Logged in as {}".format(escape(session['username']))
    return render_template("bookList.html", loggedIn=True, bookList=bookList)
  return render_template("bookList.html", loggedIn=False, bookList=bookList)

@app.route("/login", methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    session['username'] = request.form['user']
    return redirect(url_for('index'))
  return render_template('login.html')

@app.route("/logout")
def logout():
  session.pop('username', None)
  return redirect(url_for('index'))

@app.route("/signup", methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    try:
      addUser(
        db,
        request.form['username'],
        request.form['email'],
        request.form['password']
      )
    except Exception as err:
      return render_template('signup.html', loggedIn=False, error=err.args[0])
    else:
      session['username'] = request.form['username']
      return redirect(url_for('index'))
  
  if 'username' in session:
    return redirect(url_for('index'))
  return render_template('signup.html', loggedIn=False)


@app.route("/search")
def search():
  return "Search page."

@app.route("/book/isbn/<isbn>")
def bookPage(isbn):
  return "ISBN: {}".format(isbn)
