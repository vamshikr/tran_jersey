import asyncio
import json
import logging
import os
from http import HTTPStatus
from pprint import pprint
import xml.etree.ElementTree as xet

import aiohttp
from aiohttp import ClientConnectorError
from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient

from tran_jersey.exceptions import DBConnectionFailure, AppErrorCodes


class DbDriver:

    USERNAME = os.environ["MONGO_INITDB_ROOT_USERNAME"]
    PASSWORD = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
    DB_NAME = "njtransit"
    COLL_NAME = "schedule"

    def __init__(self):
        logging.info("Connecting to mongodb")
        uri = "mongodb" + "://" + DbDriver.USERNAME + ":" + DbDriver.PASSWORD + "@mongo:27017/admin"
        logging.info(uri)
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[DbDriver.DB_NAME]

    async def update(self, station2l: str, payload: dict):
        try:
            logging.info("Updating schedule for :%s", station2l)
            result = await self.db[DbDriver.COLL_NAME].update_one({"STATION_2CHAR": station2l},
                                                                  {"$set": payload},
                                                                  upsert=True)

            logging.info("Updated status: %d, %d, %d",
                         result.matched_count, result.modified_count,
                         result.upserted_id is not None)

            return result.matched_count, result.modified_count, result.upserted_id
        except ConnectionFailure as err:
            logging.exception(err)
            return 0, 0, None


class ScheduleCacher:
    INTERVAL = int(os.environ.get("CACHE_INTERVAL", "30"))
    NJT_USERNAME = os.environ["NJT_USERNAME"]
    NJT_PASSWORD = os.environ["NJT_PASSWORD"]
    NJT_TRAIN_SCHED_URL = os.environ["NJT_BASE_URL"] + "/getTrainScheduleJSON"
    RETRIES = 5

    def __init__(self, station_names: dict):
        self.all_stations = station_names
        self.db_driver = DbDriver()

    @classmethod
    def xml_to_json(cls, xml_text: str):
        json_data = json.loads(xet.XML(xml_text).text)
        return json_data["STATION"]

    @classmethod
    async def get_schedule(cls, station2l: str):

        retry_count = 0

        while retry_count < ScheduleCacher.RETRIES:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                    payload = {"username": ScheduleCacher.NJT_USERNAME,
                               "password": ScheduleCacher.NJT_PASSWORD,
                               "station": station2l}
                    async with session.post(ScheduleCacher.NJT_TRAIN_SCHED_URL,
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

    async def run(self):

        while True:
            for station2l in self.all_stations.values():
                # Call the NJTransit API
                schedule = await ScheduleCacher.get_schedule(station2l)

                if schedule:
                    await self.db_driver.update(station2l, schedule)

            await asyncio.sleep(60 * ScheduleCacher.INTERVAL)


async def start_schedule_cacher(app):
    sched_cacher = ScheduleCacher(app["all_stations"])
    asyncio.create_task(sched_cacher.run())


async def start_background_caching(app):
    asyncio.create_task(start_schedule_cacher(app))
