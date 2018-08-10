from passlib.hash import pbkdf2_sha256 as sha256

def addUser(db, username, email, password):
  """
  Add a user to the users table of the DB

  Arguments:
    db -- Session, the db object to run SQL queries on
    username -- String, the user's desired username
    email -- String, the user's email address
    password -- String, the user's password

  Errors:
  Exception -- custom message depending on error
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
    email -- String, the email to query the DB with
  """
  dbResponse = db.execute("SELECT email FROM users WHERE email = :email", {"email": email}).fetchone()

  if dbResponse == None:
    return False
  return True
