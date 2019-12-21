import asyncio
import json
import logging
import os

import uvloop
from aiohttp import web

from .njtransit import NjTransitClient
from . import google_maps

from .routes import add_routes


def init_logger(logger_level):
    """
    Initialize the logger
    :param logger_level:
    :return:
    """
    logger_format = '%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    logging.basicConfig(format=logger_format,
                        level=logger_level,
                        datefmt='%d-%m-%Y:%H:%M:%S')


def get_all_stations(stations_file: str) -> dict:
    """
    Read stations map from a file
    :param stations_file:
    :return:
    """
    with open(stations_file) as fptr:
        return json.load(fptr)


async def init_app() -> web.Application:
    """
    Initializes the application
    :return web.Application object
    """
    init_logger(os.environ.get('LOGGING_LEVEL', logging.INFO))

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    app = web.Application()

    # Checking if maps can be used for validation and zipcode lookup
    google_maps_key = os.environ.get('GOOGLE_MAPS_APIKEY', None)
    if google_maps_key:
        app['google_maps'] = google_maps.GoogleMaps(google_maps_key)
        logging.info("Google Maps service available")
    else:
        logging.error("Google Maps service NOT available")

    app["station_map"] = get_all_stations("./stationname_with_station2char.json")
    app["station_names"] = [name.casefold() for name in app["station_map"].keys()]
    app["njt_client"] = NjTransitClient(app["station_map"])

    # Adding routes
    add_routes(app)
    return app
