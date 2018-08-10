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

def login(db, name, password):
  """
  Verifies if given login credentials result in a successful login

  Arguments:
    db -- Session, the db object to run SQL queries on
    name -- String, either the username or email address
    password -- String, the user's password

  Raises:
    Exception -- Exception object whose .args[0] is the error message
  """
  invalidMsg = "Username or password is incorrect."

  if isEmail(name):
    # query the email
    dbUser = db.execute("SELECT username FROM users WHERE email = :email", {"email": name}).fetchone()
  else:
    # query the username
    dbUser = db.execute("SELECT username FROM users WHERE username = :username", {"username": name}).fetchone()
  
  if dbUser == None:
    raise Exception(invalidMsg)
  
  dbPassword = db.execute("SELECT password FROM users WHERE username = :username", {"username": dbUser}).fetchone()

  if not sha256.verify(password, dbPassword):
    raise Exception(invalidMsg)

def isEmail(_str):
  regexMatch = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", _str)
  if regexMatch == None:
    return False
  return True
