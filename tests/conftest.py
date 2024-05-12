"""Pytest configuration module"""

import time
from pathlib import Path
import uuid

import pytest
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import clear_mappers, sessionmaker

from cosmic_python import config
from cosmic_python.adapters.orm import metadata, start_mappers


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


def wait_for_sqlite_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Slqlite never came up")


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope="session")
def sqlite_db():
    engine = create_engine(config.get_sqlite_url())
    wait_for_sqlite_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session(sqlite_db):
    start_mappers()
    yield sessionmaker(bind=sqlite_db)()
    clear_mappers()


@pytest.fixture
def add_stock(sqlite_session):
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            sqlite_session.execute(
                text(
                    "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
                    " VALUES (:ref, :sku, :qty, :eta)"
                ),
                dict(ref=ref, sku=sku, qty=qty, eta=eta),
            )
            [[batch_id]] = sqlite_session.execute(
                text("SELECT id FROM batches WHERE reference=:ref AND sku=:sku"),
                dict(ref=ref, sku=sku),
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        sqlite_session.commit()

    yield _add_stock

    for batch_id in batches_added:
        sqlite_session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        sqlite_session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"),
            dict(batch_id=batch_id),
        )
    for sku in skus_added:
        sqlite_session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"),
            dict(sku=sku),
        )
        sqlite_session.commit()


@pytest.fixture
def restart_api():
    (
        Path(__file__).parents[1] / "cosmic_python" / "entrypoints" / "flask_app.py"
    ).touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"
