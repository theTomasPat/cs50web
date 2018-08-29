import os
import json

from flask import Flask, session, request, redirect, escape, url_for, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

from src.dbRunner import addUser, verifyLogin, postReview, editReview, deleteReview, getUserIDFromUsername, userReviewExists, dbBookSearch, dbBookInfo, countReviews
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
  bookList = []
  bookList.append(dbBookSearch(db, 'Random 10', ''))

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


@app.route("/search/<string:query>")
def search(query):
  bookList = []
  bookList.append(dbBookSearch(db, 'Author', query))
  bookList.append(dbBookSearch(db, 'Title', query))
  bookList.append(dbBookSearch(db, 'ISBN', query))

  return render_template("bookList.html", loggedIn=isLoggedIn(), bookList=bookList)

@app.route("/book/isbn/<isbn>", methods=['GET', 'POST'])
def bookPage(isbn):
  # This info will be needed regardless of the request method
  # the book ID for the requested ISBN is especially necessary
  dbBookInfo = dbBookInfo(db, isbn)
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

    return render_template(
      "bookPage.html",
      loggedIn=isLoggedIn(),
      book=book,
      userReviewExists=userReviewExists(
        db,
        bookID,
        getUserIDFromUsername(
          db,
          session.get('username')
        ),
        isLoggedIn()        
      )
    )
  
  # Route logic for POST request method
  elif request.method == 'POST':
    userID = getUserIDFromUsername(db, session.get('username'))
    bookID = dbBookInfo[0]
    _method = request.form['formMethod']

    if _method == 'delete':
      deleteReview(db, userID, bookID)
      print(f"User {session.get('username')} requested to delete their review")
      return redirect(f"/book/isbn/{isbn}")

    else:
      # These variables are only needed for 'post' and 'edit' methods
      _rating = request.form['rating']
      _reviewBody = request.form['reviewBody']

      if _method == 'post':
        # TODO: find and fix bug
        # publishing a review with empty form fields throws an error

        # Logic for post request
        if userReviewExists(db, bookID, userID, isLoggedIn()):
          print("Couldn't publish review because one already exists for this book by this user")
          return redirect(f"/book/isbn/{isbn}")
        else:
          postReview(db, userID, bookID, _rating, _reviewBody)
          print(f"User {session.get('username')} requested to post a review:\n{_rating}, {_reviewBody}")
          return redirect(f"/book/isbn/{isbn}")

      elif _method == 'edit':
        # Logic for edit request
        editReview(db, userID, bookID, _rating, _reviewBody)
        print(f"User {session.get('username')} requested to edit their review:\n{_rating}, {_reviewBody}")
        return redirect(f"/book/isbn/{isbn}")

@app.route('/app/<string:isbn>')
def apiGetIsbn(isbn):
  bookInfo = dbBookInfo(db, isbn)
  if bookInfo is None:
    # Flask response made from tuple (response, status, headers)
    return (json.dumps({}), 400, {'ContentType': 'application/json'})

  goodReadsInfo = bookInfoISBN(isbn)

  _title = bookInfo[2]
  _author = bookInfo[3]
  _year = bookInfo[4]
  _isbn = bookInfo[1]
  _reviewCount = countReviews(db, bookInfo[0])
  _avgRating = goodReadsInfo['average_score']

  # Flask response made from tuple (response, status, headers)
  return (
    json.dumps({
      'title': _title,
      'author': _author,
      'year': _year,
      'isbn': _isbn,
      'review_count': _reviewCount,
      'average_score': _avgRating
    }),
    200,
    {
      'ContentType': 'application/json'
    }
  )


""" Helpers """
def isLoggedIn():
  if 'username' in session:
    return True
  return False
