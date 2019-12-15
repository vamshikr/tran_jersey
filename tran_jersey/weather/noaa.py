import json
import logging
import os
from http import HTTPStatus

import aiohttp

from sure_weather.exceptions import WeatherServiceException
from sure_weather.weather.base_service import BaseWeatherService


class NoaaWeather(BaseWeatherService):
    """
    NOAA Service
    """
    SERVICE_NAME = 'noaa'
    BASE_URL_KEY = 'NOAA_URL'

    def __init__(self):
        super().__init__()
        self.url = os.environ[self.BASE_URL_KEY]

    async def _get_current_weather(self, latitude: float, longitude: float):
        """
        For a given location gets the current weather report from NOAA
        :param latitude:
        :param longitude:
        :return: json data
        """
        params = {
            'latlon': '{},{}'.format(str(latitude), str(longitude))
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + "/" + self.SERVICE_NAME, params=params) as response:
                if response.status == HTTPStatus.OK:
                    return json.loads(await response.text())

    async def get_current_temperature(self, latitude: float, longitude: float):
        """
        For a given location gets the current temperature in fahrenheit from NOAA
        :param latitude:
        :param longitude:
        :return:
        """
        try:
            report = await self._get_current_weather(latitude, longitude)
            return float(report["today"]["current"]["fahrenheit"])
        except KeyError as err:
            logging.exception(err)
            raise WeatherServiceException from err
