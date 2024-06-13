import sqlite3


# Connect to the new database
conn = sqlite3.connect('database.db', check_same_thread=False)
print("Opened new database successfully")

# Drop existing tables if they exist
conn.execute('DROP TABLE IF EXISTS Users')
conn.execute('DROP TABLE IF EXISTS Bowls')
conn.execute('DROP TABLE IF EXISTS UserBowls')
conn.execute('DROP TABLE IF EXISTS arduinos_animal')


print("Existing tables dropped successfully")

# Create tables based on the new schema

conn.execute('''CREATE TABLE Users (user_id VARCHAR(250) PRIMARY KEY NOT NULL);''')


conn.execute('''CREATE TABLE Bowls (
						animal_name VARCHAR(50) PRIMARY KEY, 
						daily_dose INTEGER, 
						bowl_weight FLOAT, 
						food_dispensed INTEGER, 
						last_food VARCHAR(250)
						);''')

conn.execute('''CREATE TABLE UserBowls (
						user_id VARCHAR(250), 
						animal_name VARCHAR(50), 
						FOREIGN KEY (user_id) REFERENCES Users(user_id), 
						FOREIGN KEY (animal_name) REFERENCES Bowls(animal_name), 
						PRIMARY KEY (user_id, animal_name)
						);''')

conn.execute('''CREATE TABLE arduinos_animal (
					arduino_id VARCHAR(250) PRIMARY KEY UNIQUE, 
					animal_name VARCHAR(50), 
					FOREIGN KEY (animal_name) REFERENCES Bowls(animal_name)
					);''')

conn.commit()

conn.close()
print("Tables created successfully")

