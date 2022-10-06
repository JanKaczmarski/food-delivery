from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from datetime import datetime
import googlemaps

app = Flask(__name__)

psql_port = "1020"

def insert_restaurant(restaurant_data):
    conn = get_db_connection()
    conn.autocommit = True
    cur = conn.cursor()
    
    
    # for every column:value pairs add their values to 
    column_query = "INSERT INTO restaurant("
    values_query = " VALUES("
    
    
    
    cur.close()
    conn.close()
    
    
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
        pass
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
    return "Hello World"

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
    global address
    if request.method == 'POST':
        address = request.form.get('address')
        # unpack locations from psycopg2.cursor.fetchall() method
        poss_addresses = [i[0] for i in get_poss_addresses()] 
        if address.lower() in poss_addresses:
            delivery_address_data = get_data(address.lower())
            return redirect(url_for('address'))
        else:
            return "No possible restaurants for that area"

    return render_template('login.html')

@app.route('/address/')
def address():
    return f"For {address.capitalize()} we have these restaurants: \n{delivery_address_data}"
