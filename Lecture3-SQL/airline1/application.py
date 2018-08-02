import os

from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
  flights = db.execute("SELECT * FROM flights").fetchall()
  return render_template("index.html", flights=flights)

@app.route("/book", methods=["POST"])
def book():
  # Create a flight booking

  # Get form info
  name = request.form.get("name")
  try:
    flight_id = int(request.form.get("flight_id"))
  except ValueError:
    return render_template("error.html", message="Invalid flight number.")
  
  # Verify that flight exists
  if db.execute("SELECT * FROM flights WHERE id = :flight_id", {"flight_id": flight_id}).returns_rows == False:
    return render_template("error.html", message="Flight does not exist.")
  
  # Update passengers table
  db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)", {"name": name, "flight_id": flight_id})
  db.commit()

  return render_template("success.html")

@app.route("/flights")
def flights():
  # Lists all flights

  flights = db.execute("SELECT * from flights").fetchall()
  return render_template("flights.html", flights=flights)

@app.route('/flights/<int:flight_id>')
def flight(flight_id):
  # Lists details about a specific flight

  # Make sure the flight exists
  flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
  if flight is None:
    return render_template("error.html", message="That flight doesn't exist!")

  # Get list of passengers on that flight
  passengers = db.execute("SELECT * FROM passengers WHERE flight_id = :flight_id", {"flight_id": flight.id}).fetchall()
  return render_template("flight.html", flight=flight, passengers=passengers)