import sqlite3

conn = sqlite3.connect('test_files/sample.db')

cur = conn.cursor()


# Create restaurants table
# cur.execute("""CREATE TABLE restaurants(
#     restaurantID INT PRIMARY KEY, name, restaurant_address,
#     open, close, deliveryRadius, tags, rating, province, description)""")
# conn.commit()


# INSERT into restaurants
# cur.execute("""INSERT INTO restaurants VALUES(
#     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
#     )""", (1, 'Halo Makaron', '9 Stefana Zeromskiego, Białystok, EMEA 15-349', '08:45 AM', '04:00 AM', 10000, 'pasta&italian&dinner type restaurant',
#            3.8, 'Podlaskie', 'Italian restaurants that serves the best pasta in the city!'))
# conn.commit()


# INSERT into addresses
# cur.execute("INSERT INTO addresses VALUES(?, ?, ?)", (1, 'Olmonty/Sezamkowa', 'Podlaskie'))
# conn.commit()

# INSERT into restaurant_address
# cur.execute("INSERT INTO restaurant_address VALUES(?, ?)", (1, 1))
# conn.commit()

cur.close()
conn.close()
