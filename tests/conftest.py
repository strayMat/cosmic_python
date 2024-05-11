"""Pytest configuration module"""

from pathlib import Path
import time
import pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from cosmic_python import config
from cosmic_python.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def restart_api():
    (Path(__file__).parents[1] / "cosmic_python" / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
