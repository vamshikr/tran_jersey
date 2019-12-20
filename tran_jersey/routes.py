import json
import logging
from pprint import pprint

from webargs import fields, validate
from webargs.aiohttpparser import parser
from aiohttp import web

from .njtransit import NjTransitClient
from .exceptions import TranJerseyException, AppErrorCodes, InputValidationException
from .helper.google_maps import GoogleMaps


class TransitOptions(web.View):
    LATITUDE_KEY = "latitude"
    LONGITUDE_KEY = "longitude"
    ORIGIN_STATION = "origin"
    DESTINATION_STATION = "destination"
    PAGE = "page"

    PAGE_SIZE = 3
    GET_ARGS = {
        ORIGIN_STATION: fields.Str(location='query', required=False),
        LATITUDE_KEY: fields.Float(location='query', required=False,
                                   validate=validate.Range(min=-90, max=90)),
        LONGITUDE_KEY: fields.Float(location='query', required=False,
                                    validate=validate.Range(min=-180, max=180)),
        DESTINATION_STATION: fields.Str(location='query', required=True),
        PAGE: fields.Int(location='query', missing=1),
    }

    async def validate_inputs(self, query_params: dict):

        errors = []

        if TransitOptions.LATITUDE_KEY not in query_params and \
                TransitOptions.LONGITUDE_KEY not in query_params \
                and TransitOptions.ORIGIN_STATION not in query_params:
            errors.append("Either origin station or origin latitude and longitude must me given")

        if TransitOptions.ORIGIN_STATION not in query_params and \
            (TransitOptions.LATITUDE_KEY not in query_params or
                TransitOptions.LONGITUDE_KEY not in query_params):
            errors.append("Either origin station or origin latitude and longitude must me given")

        if TransitOptions.LATITUDE_KEY in query_params and \
                TransitOptions.LONGITUDE_KEY in query_params \
                and TransitOptions.ORIGIN_STATION not in query_params:

            if "google_maps" in self.request.app:
                google_maps: GoogleMaps = self.request.app["google_maps"]

                if await google_maps.validate_location(query_params[TransitOptions.LATITUDE_KEY],
                                                       query_params[TransitOptions.LONGITUDE_KEY]):

                    station_nearby = await google_maps.get_train_stations(
                        query_params[TransitOptions.LATITUDE_KEY],
                        query_params[TransitOptions.LONGITUDE_KEY],
                        self.request.app["station_map"].keys())

                    if not station_nearby:
                        errors.append("No New Jersey stations found nearby")

                else:
                    errors.append("Invalid latitude and longitude")

            else:
                errors.append("Google maps service not enabled")

        if TransitOptions.ORIGIN_STATION in query_params:
            if query_params[TransitOptions.ORIGIN_STATION].casefold() not in \
                    self.request.app["station_names"]:
                errors.append("Invalid station name: {}".format(
                    query_params[TransitOptions.ORIGIN_STATION]))

        if TransitOptions.DESTINATION_STATION in query_params:
            if query_params[TransitOptions.DESTINATION_STATION].casefold() not in \
                    self.request.app["station_names"]:
                errors.append("Invalid station name: {}".format(
                    query_params[TransitOptions.DESTINATION_STATION]))

        if errors:
            raise InputValidationException(AppErrorCodes.INVALID_INPUT,
                                           '\n'.join(errors))

    async def get_njt_options(self, origin: str, destination: str, page: int) -> dict:

        all_stations: dict = self.request.app["station_map"]
        njt_client: NjTransitClient = self.request.app["njt_client"]

        full_schedule = await njt_client.get_schedule(all_stations[origin])
        pprint(full_schedule)
        filtered_schedule = [option for option in njt_client.filter_schedule(full_schedule,
                                                                             origin,
                                                                       destination.casefold())]
        logging.info(filtered_schedule)

        if len(filtered_schedule) > TransitOptions.PAGE_SIZE * (page - 1):
            start = TransitOptions.PAGE_SIZE * (page - 1)
            end = start + TransitOptions.PAGE_SIZE
            return {"schedule": njt_client.datetime_to_str(filtered_schedule[start:end])}

        return {"schedule": 0}

    async def get(self) -> web.Response:
        """
        GET method handler for /current_weather
        :return:
        """
        query_params = await parser.parse(TransitOptions.GET_ARGS, self.request)
        logging.info('Query params: %s', query_params)

        try:
            await self.validate_inputs(query_params)

            if "origin" not in query_params:
                google_maps: GoogleMaps = self.request.app["google_maps"]

                station_nearby = await google_maps.get_train_stations(
                    query_params[TransitOptions.LATITUDE_KEY],
                    query_params[TransitOptions.LONGITUDE_KEY])

                response = await self.get_njt_options(station_nearby[0],
                                                      query_params['destination'],
                                                      query_params["page"])

            response = await self.get_njt_options(query_params['origin'],
                                                  query_params['destination'],
                                                  query_params["page"])
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
    app.router.add_view("/transit/schedule", TransitOptions)
