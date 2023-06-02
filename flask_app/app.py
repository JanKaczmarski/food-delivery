from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from datetime import datetime
import googlemaps
import os
from dotenv import load_dotenv

app = Flask(__name__)

# import api_matrix_key and psql port
load_dotenv()

psql_port = os.getenv('psql_port')
api_matrix_key = os.getenv('api_matrix_key')


def check_validity(address):
    sep_address = address.split(sep='/')
    if len(sep_address) == 1:
        return False
    if len(sep_address[1].replace(" ", "")) > 0:
        # does_address_exists(essa)
        gmaps = googlemaps.Client(key=api_matrix_key)
        place_id = gmaps.find_place(input=address,
                                    input_type="textquery")['candidates'][0]['place_id']
        if gmaps.place(place_id)['status'] == 'OK':
            return True
        else:
            return False
    else:
        return False


def get_voivodeship(address):
    gmaps = googlemaps.Client(key=api_matrix_key)
    # Get voivodeship of given address, to extract smaller amount of data from db
    place_id = gmaps.find_place(input=address,
                                input_type="textquery")['candidates'][0]['place_id']
    address_components = gmaps.place(place_id)['result']['address_components']

    for component in address_components:
        if component['types'][0] == 'administrative_area_level_1':
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
        # print(values['distance']['value'])
        if distance_meters <= rest_delivery_distance[directions_result['destination_addresses'][id]]*1000:
            valid_addresses.append(
                directions_result['destination_addresses'][id])

    return valid_addresses

# route is created to display ongoing changes, will be deleted in the future


def insert_address(address):
    # Get voivodeship of given address
    # Check if restaurant can deliver food to address
    # Insert compiled data to restaurant_address table to cache the values
    conn = get_db_connection()
    conn.autocommit = True
    cur = conn.cursor()

    voivodeship = get_voivodeship(address)
    cur.execute(
        f"SELECT address, delivery_distance FROM restaurant WHERE voivodeship = '{voivodeship}';")
    fetched_data = cur.fetchall()

    # Creating new address record in database
    cur.execute('SELECT MAX(address_id) FROM address;')
    new_address_id = cur.fetchall()[0][0]
    new_address_id = int(new_address_id) + 1
    cur.execute(
        f"INSERT INTO address (address_id, address_name, voivodeship) VALUES('{new_address_id}', '{address}', '{voivodeship}')")

    # If fetched data is empty return no possible restaurants
    try:
        fetched_data[0]
        passed = True
    except IndexError:
        passed = False
    if passed:
        rest_delivery_distance = {
            tuple_of_data[0]: tuple_of_data[1] for tuple_of_data in fetched_data}
        dest_addresses = [tuple_of_data[0] for tuple_of_data in fetched_data]

        # dest_addresses = {id:{'address': address[0], 'delivery_distance': address[1]} for id, address in enumerate(cur.fetchall())}
        available_restaurants = get_available_restaurants(
            origin=address, destination=dest_addresses, rest_delivery_distance=rest_delivery_distance)
        for restaurant in available_restaurants:
            cur.execute(
                f"SELECT restaurant_id FROM restaurant WHERE address = '{restaurant}';")
            restaurant_id = cur.fetchall()[0][0]

            cur.execute(
                f"INSERT INTO restaurant_address (restaurant_id, address_id) VALUES ('{restaurant_id}', '{new_address_id}')")

        cur.close()
        conn.close()
        return {"data": {"available_restaurants": available_restaurants, "address": address}}
    else:
        cur.close()
        conn.close()
        return "No available restaurants"

    # Here connection between restaurants and address should be recorded in database, using restaurant_address
    # cur.execute()


@app.route('/partner', methods=['post', 'get'])
def become_partner():
    data = {}
    if request.method == 'POST':
        for item in request.form:
            data[item] = request.form.get(item)
        return data
    return render_template('partner.html')


def get_db_connection(db_name="locations"):
    conn = psycopg2.connect(
        host="postgresql",
        port=psql_port,
        user="postgres",
        password="password",
        dbname=db_name
    )

    return conn


def create_db():
    conn = get_db_connection(db_name="postgres")
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute('CREATE DATABASE locations;')
    except:
        return None
    cur.close()
    conn.close()
    conn = get_db_connection()
    conn.autocommit = True
    cur = conn.cursor()
    sql = open("create_tables.sql", "r")
    cur.execute(sql.read())
    sql.close()

    cur.close()
    conn.close()


def get_data(location):
    create_db()
    conn = get_db_connection()
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"""SELECT * FROM restaurant as r WHERE r.restaurant_id IN (SELECT ra.restaurant_id FROM restaurant_address as ra WHERE ra.address_id IN 
                (SELECT a.address_id FROM address as a WHERE a.address_name = '{location}'));""")
    data = cur.fetchall()

    cur.close()
    conn.close()
    return data


def get_poss_addresses():
    create_db()
    conn = get_db_connection()
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT address_name FROM address")
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data


@app.route('/')
def home():
    return "Hello World!"


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
        poss_addresses = [i[0] for i in get_poss_addresses()]
        if address.lower() in poss_addresses:
            delivery_address_data = get_data(address.lower())
            return holder(address)
        else:
            return insert_address(address.lower())

    return render_template('login.html')


@app.route('/address/')
def holder(address):
    return f"For {address.capitalize()} we have these restaurants: \n{delivery_address_data}"
