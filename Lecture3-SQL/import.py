import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
  fileToImport = open('flights.csv')
  csvReader = csv.reader(fileToImport)

  for origin, destination, duration in csvReader:
    db.execute("INSERT INTO flights (origin, destination, duration) VALUES (:origin, :destination, :duration)",
      {"origin": origin, "destination": destination, "duration": duration})
    print(f"Added flight: {origin} -> {destination} ({duration} mins)")
  db.commit()

if __name__ == "__main__":
  main()
