import os

from pytest import fixture

os.environ["NJT_USERNAME"] = "dummy_username"
os.environ["NJT_PASSWORD"] = "service-inventory"
os.environ['NJT_BASE_URL'] = "http://dummyhost.com"

from tran_jersey.app import get_all_stations

@fixture(scope='module')
def station_names():
    return get_all_stations("./stationname_with_station2char.json")

