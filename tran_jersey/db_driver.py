import os
import logging

from pymongo.errors import ConnectionFailure
from motor.motor_asyncio import AsyncIOMotorClient


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


