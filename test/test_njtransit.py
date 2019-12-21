import json
from unittest import mock

import aiohttp
import pytest
from aiohttp import web

from tran_jersey.njtransit import NjTransitClient


class MockResponse:
    def __init__(self, *args, **kwargs):
        self.status = 200

    async def text(self):
        data = {
            "?xml": {
                "@version": "1.0",
                "@encoding": "ISO-8859-1"
            },
            "STATION": {
                "STATION_2CHAR": "XC",
                "STATIONNAME": "Cranford",
                "BANNERMSGS": None,
                "ITEMS": {
                    "ITEM": [
                        {
                            "ITEM_INDEX": "0",
                            "SCHED_DEP_DATE": "20-Dec-2019 05:59:15 PM",
                            "DESTINATION": "Newark Penn",
                            "TRACK": "2",
                            "LINE": "Raritan Valley Line",
                            "TRAIN_ID": "5746",
                            "CONNECTING_TRAIN_ID": "",
                            "STATUS": "in 14 Min",
                            "SEC_LATE": "84",
                            "LAST_MODIFIED": "20-Dec-2019 05:44:41 PM",
                            "BACKCOLOR": "#FF993E",
                            "FORECOLOR": "white",
                            "SHADOWCOLOR": "black",
                            "GPSLATITUDE": "40.665911",
                            "GPSLONGITUDE": "-74.895453",
                            "GPSTIME": "20-Dec-2019 05:43:42 PM",
                            "STATION_POSITION": "1",
                            "LINEABBREVIATION": "RARV",
                            "INLINEMSG": "",
                            "STOPS": {
                                "STOP": [
                                    {
                                        "NAME": "High Bridge",
                                        "TIME": "20-Dec-2019 04:52:00 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Annandale",
                                        "TIME": "20-Dec-2019 04:56:03 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Lebanon",
                                        "TIME": "20-Dec-2019 05:00:41 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "White House",
                                        "TIME": "20-Dec-2019 05:05:23 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "North Branch",
                                        "TIME": "20-Dec-2019 05:11:45 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Raritan",
                                        "TIME": "20-Dec-2019 05:21:45 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Somerville",
                                        "TIME": "20-Dec-2019 05:25:14 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Bridgewater",
                                        "TIME": "20-Dec-2019 05:30:52 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Bound Brook",
                                        "TIME": "20-Dec-2019 05:33:58 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Dunellen",
                                        "TIME": "20-Dec-2019 05:39:12 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Plainfield",
                                        "TIME": "20-Dec-2019 05:44:39 PM",
                                        "DEPARTED": "YES",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Netherwood",
                                        "TIME": "20-Dec-2019 05:48:12 PM",
                                        "DEPARTED": "NO",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Fanwood",
                                        "TIME": "20-Dec-2019 05:51:11 PM",
                                        "DEPARTED": "NO",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Westfield",
                                        "TIME": "20-Dec-2019 05:56:03 PM",
                                        "DEPARTED": "NO",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Cranford",
                                        "TIME": "20-Dec-2019 05:59:54 PM",
                                        "DEPARTED": "NO",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Roselle Park",
                                        "TIME": "20-Dec-2019 06:05:24 PM",
                                        "DEPARTED": "NO",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Union",
                                        "TIME": "20-Dec-2019 06:09:09 PM",
                                        "DEPARTED": "NO",
                                        "STOP_STATUS": "OnTime"
                                    },
                                    {
                                        "NAME": "Newark Penn Station",
                                        "TIME": "20-Dec-2019 06:20:24 PM",
                                        "DEPARTED": "NO",
                                        "STOP_STATUS": "OnTime"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        return """<string xmlns="http://microsoft.com/webservices/">{}</string>""".format(json.dumps(data))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestNjTransitClient:

    async def test_get_schedule(self, station_names):

        with mock.patch.object(aiohttp.ClientSession, 'post', return_value=MockResponse()):
            njtransit_client = NjTransitClient(station_names)
            data = await njtransit_client.get_schedule("PV")
            assert data['STATION_2CHAR'] == 'XC'

