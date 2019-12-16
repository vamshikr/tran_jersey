import json
from datetime import datetime
import logging

from aiohttp import web

from .caching import NjTransitClient
from .exceptions import TranJerseyException, AppErrorCodes, InputValidationException


class CurrentTrains(web.View):

    def filter(self, schedule: dict, origin: str, destination: str) -> dict:

        for option in schedule["ITEMS"]["ITEM"]:

            origin_info = {
                'origin': origin,
                'departure_time': option["SCHED_DEP_DATE"]
                }

            for stop in option["STOPS"]["STOP"]:
                if stop["NAME"].casefold() == destination and stop["DEPARTED"] == "NO":
                    payload = dict({**origin_info,
                                   "destination": stop["NAME"],
                                    "arrival_time": stop["TIME"]
                                })
                    yield payload

    async def get_njt_options(self, origin: str, destination: str, page: int) -> dict:

        if origin not in self.request.app["all_stations"] or \
                destination not in self.request.app["all_stations"]:
            raise InputValidationException(AppErrorCodes.STATION_NOT_FOUND,
                                           ["Station not found"])

        all_stations: dict = self.request.app["all_stations"]
        njt_client: NjTransitClient = self.request.app["njt_client"]

        full_schedule = await njt_client.get_schedule(all_stations[origin])

        return {"schedule": [option for option in self.filter(full_schedule, origin,
                                                              destination.casefold())]}

    async def get(self) -> web.Response:
        """
        GET method handler for /current_weather
        :return:
        """
        query_params = dict(self.request.query)
        logging.info('Query params: %s', query_params)
        try:

            response = await self.get_njt_options(query_params['origin'],
                                                  query_params['destination'],
                                                  query_params.get("page", 1))
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
