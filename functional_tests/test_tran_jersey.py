import os

import pytest
import requests
from http import HTTPStatus


class TestTransJersey:

    URL = "http://localhost:8080/transit/schedule"

    def test_valid_1(self):
        response = requests.get(self.URL, params={"origin": "Aberdeen-Matawan",
                                                  "destination": "New York Penn Station"})
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert "schedule" in data and len(data["schedule"]) > 0

    def test_valid_2(self):
        """Page 2"""
        response = requests.get(self.URL, params={"origin": "Aberdeen-Matawan",
                                                  "destination": "New York Penn Station",
                                                  "page": 2})
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert "schedule" in data and len(data["schedule"]) > 0

    def test_valid_3(self):
        """using lat, lon"""
        response = requests.get(self.URL, params={"latitude": "40.575974",
                                                  "longitude": "-74.277628",
                                                  "destination": "New York Penn Station",
                                                  "page": 1})
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert "schedule" in data and len(data["schedule"]) > 0

    def test_valid_4(self):
        """valid page but out of range"""
        response = requests.get(self.URL, params={"origin": "Aberdeen-Matawan",
                                                  "destination": "New York Penn Station",
                                                  "page": 20})
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert "schedule" in data and len(data["schedule"]) == 0

    def test_invalid_1(self):
        """Invalid page"""
        response = requests.get(self.URL, params={"origin": "Aberdeen-Matawan",
                                                  "destination": "New York Penn Station",
                                                  "page": 10000})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value

    def test_invalid_2(self):
        "Invalid origin"
        response = requests.get(self.URL, params={"origin": "Aberdeen-Mawan",
                                                  "destination": "New York Penn Station",
                                                  "page": 1})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value

    def test_invalid_3(self):
        "Invalid destination"
        response = requests.get(self.URL, params={"origin": "Aberdeen-Matawan",
                                                  "destination": "New York Penn Staon",
                                                  "page": 1})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value

    def test_invalid_5(self):
        "Invalid lat, lon"
        response = requests.get(self.URL, params={"latitude": "40.575974",
                                                  "longitude": "74.277628",
                                                  "destination": "New York Penn Station",
                                                  "page": 1})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value

    def test_valid_6(self):
        "Invalid param"
        response = requests.get(self.URL, params={"latitude": "40.575974",
                                                  "longituode": "-74.277628",
                                                  "destination": "New York Penn Station",
                                                  "page": 1})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value

    def test_valid_7(self):
        "Invalid param"
        response = requests.get(self.URL, params={"latituyde": "40.575974",
                                                  "longitude": "-74.277628",
                                                  "destination": "New York Penn Station",
                                                  "page": 1})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value

    def test_valid_8(self):
        "Invalid param"
        response = requests.get(self.URL, params={"latitude": "40.575974",
                                                  "longitude": "-74.277628",
                                                  "destiyunation": "New York Penn Station",
                                                  "page": 1})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value

