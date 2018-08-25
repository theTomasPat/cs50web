import os

from flask import Flask, session, request, redirect, escape, url_for, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from src.dbRunner import addUser, verifyLogin
from src.GoodReads import bookInfoISBN

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

  return render_template("bookList.html", loggedIn=isLoggedIn(), bookList=bookList)

@app.route("/login", methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    try:
      verifyLogin(
        db,
        request.form['user'],
        request.form['password']
      )
    except Exception as err:
      #print(err)
      return render_template('login.html', loggedIn=False, error=err.args[0])
    else:
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
  
  if isLoggedIn():
    return redirect(url_for('index'))
  return render_template('signup.html', loggedIn=False)


@app.route("/search")
def search():
  return "Search page."

@app.route("/book/isbn/<isbn>", methods=['GET', 'POST', 'DELETE'])
def bookPage(isbn):
  # This info will be needed regardless of the request method
  # the book ID for the requested ISBN is especially necessary
  dbBookInfo = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
  if dbBookInfo == None:
    return render_template("bookPage.html", loggedIn=isLoggedIn(), book=None, error="That book can't be found!")

  # Route logic for GET request method
  if request.method == 'GET':
    bookID = dbBookInfo[0]
    dbBookReviews = db.execute("SELECT user_id, rating, description FROM reviews WHERE book_id = :bookID", {"bookID": bookID}).fetchall()
    if dbBookReviews != None:
      processedReviews = []
      for review in dbBookReviews:
        user = db.execute("SELECT username FROM users WHERE id=:id", {"id": review[0]}).fetchone()[0]
        processedReviews.append((user, review[1], review[2]))

    goodReadsBookInfo = bookInfoISBN(isbn)

    # Build the book object that will be passed into the html template
    book = {
      "isbn": dbBookInfo[1],
      "coverImage": goodReadsBookInfo['image_url'],
      "title": dbBookInfo[2],
      "author": dbBookInfo[3],
      "year": dbBookInfo[4],
      "description": goodReadsBookInfo['description'],
      "average_score": goodReadsBookInfo['average_score'],
      "reviews": processedReviews
    }

    return render_template("bookPage.html", loggedIn=isLoggedIn(), book=book, userReviewExists=userReviewExists(bookID, getUserIDFromUsername()))
  
  # Route logic for POST request method
  elif request.method == 'POST':
    userID = getUserIDFromUsername()
    bookID = dbBookInfo[0]
    _method = request.form['formMethod']

    if _method == 'delete':
      # Logic for delete request
      db.execute("DELETE FROM reviews WHERE user_id=:userID AND book_id=:bookID", {
        "userID": userID,
        "bookID": bookID
      })
      db.commit()

      print(f"User {session.get('username')} requested to delete their review")
      return redirect(f"/book/isbn/{isbn}")

    else:
      # These variables are only needed for 'post' and 'edit' methods
      _rating = request.form['rating']
      _reviewBody = request.form['reviewBody']

      if _method == 'post':
        # Logic for post request
        if userReviewExists(bookID, userID):
          print("Couldn't publish review because one already exists for this book by this user")
          return redirect(f"/book/isbn/{isbn}")
        else:
          db.execute("INSERT INTO reviews (user_id, book_id, rating, description) VALUES (:user_id, :book_id, :rating, :desc)", {
            "user_id": userID,
            "book_id": bookID,
            "rating":  _rating,
            "desc":    _reviewBody
          })
          db.commit()

          print(f"User {session.get('username')} requested to post a review:\n{_rating}, {_reviewBody}")
          return redirect(f"/book/isbn/{isbn}")

      elif _method == 'edit':
        # Logic for edit request
        # TODO: add db call to edit user's review for this book
        db.execute("UPDATE reviews SET rating=:rating, description=:desc WHERE user_id=:userID AND book_id=:bookID", {
          "rating": _rating,
          "desc":   _reviewBody,
          "userID": userID,
          "bookID": bookID
        })
        db.commit()

        print(f"User {session.get('username')} requested to edit their review:\n{_rating}, {_reviewBody}")
        return redirect(f"/book/isbn/{isbn}")
    

""" Helpers """
def isLoggedIn():
  if 'username' in session:
    return True
  return False

def getUserIDFromUsername():
  userID = db.execute("SELECT id FROM users WHERE username = :username", {"username": session.get('username')}).fetchone()[0]
  print(f"Retrieved user ID from {session.get('username')}: {userID}")
  return userID

def userReviewExists(book_id, user_id):
  if isLoggedIn():
    userReviews = db.execute("SELECT id FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id": user_id, "book_id": book_id}).fetchone()
    return False if userReviews == None else True
  return False
