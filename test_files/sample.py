from email import header
import googlemaps
from pprint import pprint
import requests
from json import loads
#address = "Białystok/Nowe Miasto"
api_matrix_key = ''

def check_validity(address):
    sep_address = address.split(sep='/')
    if len(sep_address) == 1:
        return False
    if len(sep_address[1].replace(" ", "")) > 0:
        #does_address_exists(essa)
        gmaps = googlemaps.Client(key=api_matrix_key)
        place_id = gmaps.find_place(input=address,
                                    input_type="textquery")['candidates'][0]['place_id']
        if gmaps.place(place_id)['status'] == 'OK':
            return True
        else:
            return False
    else:
        return False


def check_rest_address(address):
    payload = {}
    headers = {}

    # Check if given address is that of a restaurant

    gmaps = googlemaps.Client(key=api_matrix_key)
    place_id = gmaps.find_place(input=address,
                                input_type="textquery")['candidates'][0]['place_id']
    address_components = gmaps.place(place_id)['result']['address_components']
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name%2Crating%2Cformatted_phone_number&key={api_matrix_key}"

    response = requests.request("GET", url, headers=headers, data=payload)
    output = loads(response.text)
    try:
        output['result']['rating']
        return True
    except KeyError:
        return False