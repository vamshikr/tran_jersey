import logging
from http import HTTPStatus

import aiohttp


class GoogleMaps:
    """
    Google maps interface
    """
    HOST_NAME = 'maps.googleapis.com'
    HEADERS = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache'
    }

    def __init__(self, api_key):
        self.api_key = api_key

    async def validate_location(self, latitude: float, longitude: float) -> bool:
        """
        checking if a latitude, longitude is valid or not
        :param latitude:
        :param longitude:
        :return:
        """
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
        """
        Get nearest train station for given lat, lon
        :param latitude:
        :param longitude:
        :param valid_stations:
        :return:
        """
        params = {
            'location': '{},{}'.format(latitude, longitude),
            'key': self.api_key,
            'type': "train_station",
            "radius": "1600"
        }

        logging.info("Getting train stations near (%f, %f)", latitude, longitude)

        async with aiohttp.ClientSession() as session:
            async with session.post('https://maps.googleapis.com/maps/api/place/nearbysearch/json',
                                    params=params) as response:
                if response.status == HTTPStatus.OK:
                    payload = await response.json()
                    if payload['status'] == 'OK':
                        if valid_stations:
                            return [result["name"] for result in payload["results"]
                                    if result["name"] in valid_stations]

                        return [result["name"] for result in payload["results"]]

        return []
