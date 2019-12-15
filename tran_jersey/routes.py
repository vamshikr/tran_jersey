import json
from datetime import datetime
import logging

from aiohttp import web

from .exceptions import TranJerseyException


class CurrentWeather(web.View):

    async def get(self) -> web.Response:
        """
        GET method handler for /current_weather
        :return:
        """
        query_params = dict(self.request.query)
        logging.info('Query params: %s', query_params)
        try:

            response = {
                "dummy": True,
                "curr_dt": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
            }
            logging.info(response)
            return web.json_response(response)

        except TranJerseyException as err:
            return web.Response(status=err.HTTP_CODE,
                                content_type="application/json",
                                text=json.dumps(err.to_dict()))


def add_routes(app: web.Application):
    """
    Add routes
    :param app:
    :return:
    """
    app.router.add_view("/current_weather", CurrentWeather)
