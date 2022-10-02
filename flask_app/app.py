from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

psql_port = "5432"

def create_db(db_name):
    conn = psycopg2.connect(
            host='postgresql',
            port=psql_port,
            user='postgres',
            password='password'
        )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute('CREATE DATABASE locations;')
    except:
        pass
    cur.close()
    conn.close()
    conn = psycopg2.connect(
                host='postgresql',
                port=psql_port,
                user='postgres',
                password='password',
                dbname=db_name)
    conn.autocommit = True
    cur = conn.cursor()
    sql = open("create_tables.sql", "r")
    cur.execute(sql.read())
    sql.close()
    
    cur.close()
    conn.close()

def get_data(location, db_name):
    create_db(db_name)
    conn = psycopg2.connect(
        host='postgresql',
        port=psql_port,
        user='postgres',
        password='password',
        dbname=db_name)
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM test;')
    data = cur.fetchall()
    
    cur.close()
    conn.close() 
    return data   

@app.route('/')
def home():
    return "Hello World"

@app.route('/login/', methods=['post', 'get'])
def login():
    global poss_restaurants
    global address
    poss_restaurants = []
    if request.method == 'POST':
        address = request.form.get('address').capitalize()
        delivery_address_data = get_data(address, "locations")
        # Here should be a request to database with possible restaurants for given address
        if address.lower() == 'olmonty':
            poss_restaurants = ["Halo Sushi", "Halo Pizza", "Gorący Trójkąt", delivery_address_data]
            return redirect(url_for('address'))
        else:
            return "No possible restaurants"

    return render_template('login.html', poss_restaurants=poss_restaurants)

@app.route('/address/')
def address():
    return f"For {address} we have these restaurants: \n{poss_restaurants}"