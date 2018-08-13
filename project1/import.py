import sys
import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import src.GoodReads

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

""" Read the rows from the given file and add them to the DB """
""" Assume the first row in the CSV is a header """
def main(fileToImport):
  with open(fileToImport) as infile:
    csvReader = csv.reader(infile)
    next(csvReader, None)

    count = 1

    for entry in csvReader:
      db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {
        "isbn": entry[0],
        "title": entry[1],
        "author": entry[2],
        "year": entry[3]
        })

      print(f"{count}: Adding {entry[1]} by {entry[2]}")
      count += 1
      
    db.commit()
    print("Import complete")

if __name__ == "__main__":
  if len(sys.argv) < 2:
    raise ValueError("A file must be given to import from")

  main(sys.argv[1])