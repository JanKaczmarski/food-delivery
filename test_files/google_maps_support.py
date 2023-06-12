from email import header
import googlemaps
from pprint import pprint
import requests
from json import loads
from datetime import datetime
import unicodedata

# address = "Białystok/Nowe Miasto"
api_matrix_key = 'AIzaSyD9HmY5GR0zaOef0TBODBGIwjUNlmqC9HI'

now = datetime.now()
gmaps = googlemaps.Client(api_matrix_key)

directions_result = gmaps.distance_matrix(origins='olmonty/jaworowa',
                                          destinations='9 Stefana Zeromskiego , 15-349 Bialystok, Poland',
                                          mode="driving",
                                          departure_time=now)

pprint(directions_result)
