import requests
from json import loads
import googlemaps




def check_rest_address(address, api_key):
    payload = {}
    headers = {}

    # Check if given address is that of a restaurant

    gmaps = googlemaps.Client(key=api_key)
    place_id = gmaps.find_place(input=address,
                                input_type="textquery")['candidates'][0]['place_id']
    address_components = gmaps.place(place_id)['result']['address_components']
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name%2Crating%2Cformatted_phone_number&key={api_key}"

    response = requests.request("GET", url, headers=headers, data=payload)
    output = loads(response.text)
    try:
        output['result']['rating']
        return True
    except KeyError:
        return False