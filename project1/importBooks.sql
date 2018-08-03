CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  isbn VARCHAR NOT NULL,
  title VARCHAR NOT NULL,
  author VARCHAR NOT NULL,
  year INTEGER NOT NULL,
  average_score NUMERIC(3, 2),
  review_count INTEGER,
  image_url VARCHAR
);