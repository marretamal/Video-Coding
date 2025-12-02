import os
import pytest
from fastapi.testclient import TestClient
from practice1 import app  # your API

client = TestClient(app)

# Path to a sample small test video
TEST_VIDEO = "test_files/sample.mp4"

@pytest.mark.parametrize("codec", ["vp8", "vp9", "h265"])
def test_transcode_video(codec):
    with open(TEST_VIDEO, "rb") as f:
        response = client.post(f"/transcode-video?codec={codec}",
                               files={"file": ("sample.mp4", f, "video/mp4")})

    assert response.status_code == 200
    assert len(response.content) > 1000  # output file exists


def test_encoding_ladder():
    with open(TEST_VIDEO, "rb") as f:
        response = client.post("/encoding-ladder",
                               files={"file": ("sample.mp4", f, "video/mp4")})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
