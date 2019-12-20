import asyncio
import json
import logging
import os
import re
from datetime import datetime
from http import HTTPStatus
import xml.etree.ElementTree as xet
import pytz

import aiohttp
from aiohttp import ClientConnectorError

from tran_jersey.db_driver import DbDriver
from tran_jersey.exceptions import AppErrorCodes, NjTransitException


class NjTransitClient:
    INTERVAL = int(os.environ.get("CACHE_INTERVAL", "30"))
    NJT_USERNAME = os.environ["NJT_USERNAME"]
    NJT_PASSWORD = os.environ["NJT_PASSWORD"]
    NJT_TRAIN_SCHED_URL = os.environ["NJT_BASE_URL"] + "/getTrainScheduleJSON"
    RETRIES = 5
    DATETIME_ATTRIBUTES = ["ITEMS/ITEM/GPSTIME",
                           "ITEMS/ITEM/SCHED_DEP_DATE",
                           "ITEMS/ITEM/LAST_MODIFIED",
                           "ITEMS/ITEM/STOPS/STOP/TIME"]
    TRIE_STRUCT = None
    EST = pytz.timezone('US/Eastern')
    DATETIME_FORMAT = "%d-%b-%Y %I:%M:%S %p"

    def __new__(cls, *args, **kwargs):
        cls.TRIE_STRUCT = cls.construct_trie(cls.DATETIME_ATTRIBUTES)
        return super(NjTransitClient, cls).__new__(cls)

    def __init__(self, station_names: dict):
        self.all_stations = station_names
        self.db_driver = DbDriver()

    @classmethod
    def get_key(cls, parent, child):
        """
        :param parent:
        :param child:
        :return:
        """
        if parent:
            return f'{parent}/{child}'

        return child

    @classmethod
    def construct_trie(cls, keys: list) -> set:
        """
        This method creates a trie Data structure
        :param keys:
        :return:
        """
        trie_struct = set(keys)

        for key in keys:
            trie_struct.update((key[0:m.start()] for m in re.finditer(r'[/]', key)))

        return trie_struct

    @classmethod
    def parse_datetime(cls, parent: str, child):
        """
        Parsing the trie DS
        :param parent:
        :param child:
        :return:
        """
        if parent == '' or parent in cls.TRIE_STRUCT:

            if isinstance(child, dict):
                for key, val in child.items():
                    child[key] = cls.parse_datetime(cls.get_key(parent, key), val)
            elif isinstance(child, list):
                child = [cls.parse_datetime(parent, val) for val in child]
            elif isinstance(child, str):
                child = datetime.strptime(child, cls.DATETIME_FORMAT).replace(tzinfo=cls.EST).\
                    astimezone(pytz.UTC)
            else:
                logging.error("###Type not recognized: %s=%s", parent, child)

        return child

    @classmethod
    def filter_schedule(cls, schedule: dict, origin: str, destination: str) -> dict:

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

    @classmethod
    def xml_to_json(cls, xml_text: str):
        json_data = json.loads(xet.XML(xml_text).text)
        #return cls.parse_datetime('', json_data["STATION"])
        return json_data["STATION"]

    @classmethod
    async def get_schedule(cls, station2l: str):

        retry_count = 0

        while retry_count < NjTransitClient.RETRIES:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    payload = {"username": NjTransitClient.NJT_USERNAME,
                               "password": NjTransitClient.NJT_PASSWORD,
                               "station": station2l}
                    async with session.post(NjTransitClient.NJT_TRAIN_SCHED_URL,
                                            headers=headers, data=payload, ssl=False) as response:

                        if response.status == HTTPStatus.OK:
                            response_body = await response.text()
                            return cls.xml_to_json(response_body)

                        logging.info("Registration failure %s", await response.text())

            except ClientConnectorError as err:
                logging.exception(err)
            finally:
                retry_count += 1
                await asyncio.sleep(1)

        raise NjTransitException(AppErrorCodes.SERVICE_NOT_AVAILABLE,
                                 "Failed to get schedule from {}".format(
                                     NjTransitClient.NJT_TRAIN_SCHED_URL))

    async def run(self):

        while True:
            for station2l in self.all_stations.values():
                # Call the NJTransit API
                schedule = await NjTransitClient.get_schedule(station2l)

                if schedule:
                    await self.db_driver.update(station2l, schedule)

            await asyncio.sleep(60 * NjTransitClient.INTERVAL)


async def start_schedule_cacher(app):
    sched_cacher = NjTransitClient(app["station_map"])
    asyncio.create_task(sched_cacher.run())


async def start_background_caching(app):
    asyncio.create_task(start_schedule_cacher(app))
