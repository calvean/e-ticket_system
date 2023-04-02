-- prepares a MySQL server for the project
CREATE DATABASE IF NOT EXISTS tickets;
CREATE USER IF NOT EXISTS 'test'@'localhost' IDENTIFIED WITH mysql_native_password BY 'pswd';
GRANT ALL ON `test`.* TO 'test'@'localhost'
GRANT SELECT ON `performance_schema`.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

-- prepares the necessary tables

USE tickets;

CREATE TABLE events (
  id INT(11) NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  time TIME NOT NULL,
  location VARCHAR(255) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  description TEXT NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE tickets (
  id INT(11) NOT NULL AUTO_INCREMENT,
  event_id INT(11) NOT NULL,
  email VARCHAR(255) NOT NULL,
  quantity INT(11) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (event_id) REFERENCES events(id)
);

CREATE TABLE users (
  id INT(11) NOT NULL AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY (email)
);

CREATE TABLE payments (
  id INT(11) NOT NULL AUTO_INCREMENT,
  ticket_id INT(11) NOT NULL,
  payment_id VARCHAR(255) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);

