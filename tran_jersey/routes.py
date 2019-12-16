import json
from datetime import datetime
import logging

from aiohttp import web

from .caching import NjTransitClient
from .exceptions import TranJerseyException, AppErrorCodes, InputValidationException


class CurrentTrains(web.View):

    async def get_njt_options(self, origin: str, destination: str, timestamp=None) -> dict:

        if origin not in self.request.app["all_stations"] or \
                destination not in self.request.app["all_stations"]:
            raise InputValidationException(AppErrorCodes.STATION_NOT_FOUND,
                                           ["Station not found"])

        all_stations: dict = self.request.app["all_stations"]
        njt_client: NjTransitClient = self.request.app["njt_client"]

        schedule = await njt_client.get_schedule(all_stations[origin])

        return schedule

    async def get(self) -> web.Response:
        """
        GET method handler for /current_weather
        :return:
        """
        query_params = dict(self.request.query)
        logging.info('Query params: %s', query_params)
        try:

            response = await self.get_njt_options(query_params['origin'],
                                            query_params['destination'])
            #logging.info(response)
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
    app.router.add_view("/current_weather", CurrentTrains)
