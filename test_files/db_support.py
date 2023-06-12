import sqlite3

conn = sqlite3.connect('flask_app/main.db')

cur = conn.cursor()

cur.execute(
    "INSERT INTO restaurant_address(addressID, restaurantID) VALUES (2, 1)")
conn.commit()

cur.close()
conn.close()
