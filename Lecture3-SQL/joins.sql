CREATE TABLE passengers (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  flight_id INTEGER REFERENCES flights
);

INSERT INTO passengers (name, flight_id) VALUES ('Alice', 1);
INSERT INTO passengers (name, flight_id) VALUES ('Bob', 1);
INSERT INTO passengers (name, flight_id) VALUES ('Charlie', 2);
INSERT INTO passengers (name, flight_id) VALUES ('David', 2);
INSERT INTO passengers (name, flight_id) VALUES ('Neo', 4);
INSERT INTO passengers (name, flight_id) VALUES ('Sam', 6);
INSERT INTO passengers (name, flight_id) VALUES ('Tomas', 6);