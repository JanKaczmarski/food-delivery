from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import googlemaps
import os
from dotenv import load_dotenv


app = Flask(__name__)

# import api_matrix_key and psql port
load_dotenv()

api_matrix_key = os.getenv('api_matrix_key')


def check_validity(address):
    sep_address = address.split(sep='/')
    if len(sep_address) == 1:
        return False
    if len(sep_address[1].replace(" ", "")) > 0:
        gmaps = googlemaps.Client(key=api_matrix_key)
        place_id = gmaps.find_place(input=address,
                                    input_type="textquery")['candidates'][0]['place_id']
        if gmaps.place(place_id)['status'] == 'OK':
            return True
        else:
            return False
    else:
        return False


def get_province(address):
    gmaps = googlemaps.Client(key=api_matrix_key)
    place_id = gmaps.find_place(input=address,
                                input_type="textquery")['candidates'][0]['place_id']
    address_components = gmaps.place(place_id)['result']['address_components']

    for component in address_components:
        if component['types'][0] == 'administrative_area_level_1':
            # Voivodeship == province
            return component['long_name'].replace(" Voivodeship", "")
    raise Exception("Invalid address")


def get_available_restaurants(origin, destination, rest_delivery_distance):
    now = datetime.now()
    # create google maps instance to call methods on it, passing my api key
    gmaps = googlemaps.Client(key=api_matrix_key)
    directions_result = gmaps.distance_matrix(origins=origin,
                                              destinations=destination,
                                              mode="driving",
                                              departure_time=now)

    valid_addresses = []
    for id, values in enumerate(directions_result['rows'][0]['elements']):
        distance_meters = values['distance']['value']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT restaurantID FROM restaurants WHERE restaurantADDRESS = ?",
                    (directions_result['destination_addresses'][id],))

        if distance_meters <= rest_delivery_distance[cur.fetchone()[0]]:
            valid_addresses.append(
                directions_result['destination_addresses'][id])

        close_conn(conn, cur)

    return valid_addresses


def insert_address(address):
    # Get province of given address
    # Check if restaurant can deliver food to address
    # Insert compiled data to restaurant_address table to cache the values
    conn = get_db_connection()
    cur = conn.cursor()

    province = get_province(address)
    cur.execute(
        "SELECT restaurantID, deliveryRadius, restaurantAddress FROM restaurants WHERE province = ?;", (province,))
    fetched_data = cur.fetchall()

    # Creating new address record in database
    cur.execute('SELECT MAX(addressID) FROM addresses;')
    new_address_id = cur.fetchall()[0][0]
    new_address_id = int(new_address_id) + 1
    cur.execute(
        "INSERT INTO addresses (addressID, address, province) VALUES(?, ?, ?)", (new_address_id, address, province))
    conn.commit()

    # If fetched data is empty return no possible restaurants
    try:
        fetched_data[0]
        passed = True
    except IndexError:
        passed = False
    if passed:
        rest_delivery_distance = {
            tuple_of_data[0]: tuple_of_data[1] for tuple_of_data in fetched_data}
        dest_addresses = [tuple_of_data[2] for tuple_of_data in fetched_data]

        available_restaurants = get_available_restaurants(
            origin=address, destination=dest_addresses, rest_delivery_distance=rest_delivery_distance)

        for restaurant in available_restaurants:
            cur.execute(
                "SELECT restaurantID FROM restaurants WHERE restaurantAddress = ?;", (restaurant,))
            restaurant_id = cur.fetchall()[0][0]

            cur.execute(
                "INSERT INTO restaurant_address (restaurantID, addressID) VALUES (?, ?)", (restaurant_id, new_address_id))
            conn.commit()
        cur.close()
        conn.close()
        return {"data": {"available_restaurants": available_restaurants, "address": address}}
    else:
        cur.close()
        conn.close()
        return "No available restaurants"


def get_db_connection(db="./main.db"):
    conn = sqlite3.connect(db)
    return conn


def close_conn(conn, cur):
    cur.close()
    conn.close()


def get_data(location):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""SELECT * FROM restaurants as r WHERE r.restaurantID IN (SELECT ra.restaurantID FROM restaurant_address as ra WHERE ra.addressID IN 
                (SELECT a.addressID FROM addresses as a WHERE LOWER(a.address) = ?));""", (location,))
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


def get_poss_addresses():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT address FROM addresses")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


@app.route('/')
def home():
    return f"Hello World!"


@app.route('/partner', methods=['post', 'get'])
def become_partner():
    data = {}
    if request.method == 'POST':
        for item in request.form:
            data[item] = request.form.get(item)
        return data
    return render_template('partner.html')


@app.route('/restaurant', methods=['post', 'get'])
def restaurant():
    data = {}
    if request.method == 'POST':
        for item in request.form:
            data[item] = (request.form.get(item))
        return data
    return render_template('restaurant.html', data=data)


@app.route('/login/', methods=['post', 'get'])
def login():
    global delivery_address_data
    if request.method == 'POST':
        address = request.form.get('address')

        if check_validity(address) is False:
            return "Invalid address"
        # unpack locations from psycopg2.cursor.fetchall() method
        poss_addresses = [i[0].lower() for i in get_poss_addresses()]
        if address.lower() in poss_addresses:
            delivery_address_data = get_data(address.lower())
            return holder(address, delivery_address_data)
        else:
            return insert_address(address.lower())

    return render_template('login.html')


@app.route('/address/')
def holder(address, delivery_address_data):
    return f"For {address.capitalize()} we have these restaurants: \n{delivery_address_data}"
