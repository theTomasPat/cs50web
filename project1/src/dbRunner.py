import re
from passlib.hash import pbkdf2_sha256 as sha256

def addUser(db, username, email, password):
  """
  Add a user to the users table of the DB

  Arguments:
    db -- Session, the db object to run SQL queries on
    username -- String, the user's desired username
    email -- String, the user's email address
    password -- String, the user's password

  Raises:
    Exception -- Exception object whose .args[0] is the error message
  """
  
  if userExists(db, username):
    raise Exception("Username is already taken!")
  
  if emailExists(db, email):
    raise Exception("There is already an account associated with that email.")

  '''if not validPassword(password):
    raise Exception("Please enter a valid password")'''

  hashedPass = sha256.hash(password)

  db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
    {
      'username': username,
      'email': email,
      'password': hashedPass
    }
  )
  db.commit()

def userExists(db, username):
  """
  Query the DB and return True if the username already exists, otherwise False

  Arguments:
    db -- Session, the db object to run SQL queries on
    username -- String, the username to query the DB with

  Returns:
    Boolean -- whether or not the username already exists
  """
  dbResponse = db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchone()

  if dbResponse == None:
    return False
  return True

def emailExists(db, email):
  """
  Query the DB and return True if the email exists, otherwise False

  Arguments:
    db -- Session, the db object to run SQL queries on
    email -- String, the email to query the DB with
  """
  dbResponse = db.execute("SELECT email FROM users WHERE email = :email", {"email": email}).fetchone()

  if dbResponse == None:
    return False
  return True

def verifyLogin(db, handle, password):
  """
  Verifies if given login credentials result in a successful login

  Arguments:
    db -- Session, the db object to run SQL queries on
    handle -- String, either the username or email address
    password -- String, the user's password

  Raises:
    Exception -- Exception object whose .args[0] is the error message
  """
  invalidMsg = "Username or password is incorrect."

  if isEmail(handle):
    # query the email
    print(f"Querying DB with email: {handle}")
    dbUser = db.execute("SELECT username FROM users WHERE email = :email", {"email": handle}).fetchone()
  else:
    # query the username
    print(f"Querying DB with username: {handle}")
    dbUser = db.execute("SELECT username FROM users WHERE username = :username", {"username": handle}).fetchone()
  
  if dbUser == None:
    print("Username/email wasn't found")
    raise Exception(invalidMsg)
  
  print(f"Grabbing hashed password where username: {dbUser[0]}")
  dbPassword = db.execute("SELECT password FROM users WHERE username = :username", {"username": dbUser[0]}).fetchone()[0]

  if not sha256.verify(password, dbPassword.__str__()):
    print("Password was incorrect")
    raise Exception(invalidMsg)

def isEmail(_str):
  regexMatch = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", _str)
  if regexMatch == None:
    return False
  return True

def getUserIDFromUsername(db, username):
  userID = db.execute("SELECT id FROM users WHERE username = :username", {"username": username}).fetchone()[0]
  print(f"Retrieved user ID from {username}: {userID}")
  return userID

def userReviewExists(db, book_id, user_id, loggedIn):
  if loggedIn:
    userReviews = db.execute("SELECT id FROM reviews WHERE user_id = :user_id AND book_id = :book_id", {"user_id": user_id, "book_id": book_id}).fetchone()
    return False if userReviews == None else True
  return False

def postReview(db, user_id, book_id, rating, body):
  db.execute("INSERT INTO reviews (user_id, book_id, rating, description) VALUES (:user_id, :book_id, :rating, :desc)", {
    "user_id": user_id,
    "book_id": book_id,
    "rating":  rating,
    "desc":    body
  })
  db.commit()

def editReview(db, user_id, book_id, rating, body):
  db.execute("UPDATE reviews SET rating=:rating, description=:desc WHERE user_id=:userID AND book_id=:bookID", {
    "rating": rating,
    "desc":   body,
    "userID": user_id,
    "bookID": book_id
  })
  db.commit()

def deleteReview(db, user_id, book_id):
  db.execute("DELETE FROM reviews WHERE user_id=:userID AND book_id=:bookID", {
    "userID": user_id,
    "bookID": book_id
  })
  db.commit()
