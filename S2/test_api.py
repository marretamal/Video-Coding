import unittest
from fastapi.testclient import TestClient
from practice1 import app

client = TestClient(app)

class TestAPI(unittest.TestCase):

    def test_rgb_to_yuv(self):
        r = client.get("/rgb-to-yuv?r=100&g=150&b=200")
        assert r.status_code == 200
        data = r.json()
        assert "y" in data

    def test_yuv_to_rgb(self):
        r = client.get("/yuv-to-rgb?y=140&u=128&v=128")
        assert r.status_code == 200
        assert "r" in r.json()

    