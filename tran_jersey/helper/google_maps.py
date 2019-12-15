import logging
from http import HTTPStatus

import aiohttp


class GoogleMaps:

    HOST_NAME = 'maps.googleapis.com'
    HEADERS = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache'
    }

    def __init__(self, api_key):
        self.api_key = api_key

    async def validate_location(self, latitude: float, longitude: float):

        params = {
            'latlng': '{},{}'.format(latitude, longitude),
            'key': self.api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://maps.googleapis.com/maps/api/geocode/json',
                                    params=params) as response:
                if response.status == HTTPStatus.OK and (await response.json())['status'] == 'OK':
                    return True

        return False

    async def get_latlon(self, zipcode: int) -> tuple:

        params = {
            'address': zipcode,
            'key': self.api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://maps.googleapis.com/maps/api/geocode/json',
                                    params=params) as response:
                if response.status == HTTPStatus.OK:
                    data = await response.json()
                    logging.info(data)
                    if data['results']:
                        location = data["results"][0]["geometry"]["location"]
                        return location["lat"], location["lng"]

        raise ValueError(f'Invalid zipcode: {zipcode}')
