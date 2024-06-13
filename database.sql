PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE Users (user_id VARCHAR(250) PRIMARY KEY NOT NULL);
INSERT INTO Users VALUES(1);
CREATE TABLE Bowls (animal_name VARCHAR(50) PRIMARY KEY, daily_dose INTEGER, bowl_weight FLOAT, food_dispensed INTEGER, last_food VARCHAR(250));
INSERT INTO Bowls VALUES('Cat',50.0,500.0,200.0,'2024-05-10 08:00:00');
CREATE TABLE UserBowls (user_id INTEGER, animal_name VARCHAR(50), FOREIGN KEY (user_id) REFERENCES Users(user_id), FOREIGN KEY (animal_name) REFERENCES Bowls(animal_name), PRIMARY KEY (user_id, animal_name));
INSERT INTO UserBowls VALUES(1,'Cat');
CREATE TABLE arduinos_animal (arduino_id VARCHAR(250) PRIMARY KEY UNIQUE, animal_name VARCHAR(50), FOREIGN KEY (animal_name) REFERENCES Bowls(animal_name));
INSERT INTO arduinos_animal VALUES(1,'Cat');

COMMIT;
