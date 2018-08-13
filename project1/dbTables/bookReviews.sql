CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users,
  book_id INTEGER REFERENCES books,
  rating INTEGER NOT NULL,
  description VARCHAR NOT NULL
);