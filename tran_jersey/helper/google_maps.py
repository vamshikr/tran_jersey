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

    async def validate_location(self, latitude: float, longitude: float) -> bool:

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

    async def get_train_stations(self, latitude: float, longitude: float,
                                 valid_stations=None) -> list:

        params = {
            'location': '{},{}'.format(latitude, longitude),
            'key': self.api_key,
            'type': "train_station",
            "radius": "1600"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://maps.googleapis.com/maps/api/place/nearbysearch/json',
                                    params=params) as response:
                if response.status == HTTPStatus.OK:
                    payload = await response.json()
                    if payload['status'] == 'OK':
                        if valid_stations:
                            return [result["name"] for result in payload["result"]
                                    if result["name"] in valid_stations]
                        else:
                            return [result["name"] for result in payload["result"]]

        return []
