CREATE TABLE passengers (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  flight_id INTEGER REFERENCES flights
);

INSERT INTO passengers (name, flight_id) VALUES ('Alice', 8);
INSERT INTO passengers (name, flight_id) VALUES ('Bob', 8);
INSERT INTO passengers (name, flight_id) VALUES ('Charlie', 3);
INSERT INTO passengers (name, flight_id) VALUES ('David', 3);
INSERT INTO passengers (name, flight_id) VALUES ('Neo', 4);
INSERT INTO passengers (name, flight_id) VALUES ('Sam', 5);
INSERT INTO passengers (name, flight_id) VALUES ('Tomas', 5);