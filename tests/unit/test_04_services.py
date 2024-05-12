from datetime import datetime, timedelta

import pytest

import cosmic_python.domain.model as model
import cosmic_python.service_layer.services as services
from cosmic_python.adapters.repository import FakeRepository
from tests.conftest import random_sku


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_commits():
    repo = FakeRepository.for_batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    session = FakeSession()

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


def test_returns_allocation():
    repo = FakeRepository.for_batch("b1", "COMPLICATED-LAMP", 100)  # (1)

    result = services.allocate(
        "o1", "COMPLICATED-LAMP", 10, repo, FakeSession()
    )  # (2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    repo = FakeRepository.for_batch("b1", "AREALSKU", 100)  # (1)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())  # (2) (3)


def test_error_out_of_stock():
    sku = random_sku()
    repo = FakeRepository.for_batch("b1", sku, 10)

    with pytest.raises(model.OutOfStock, match=f"Out of stock for line {sku}"):
        services.allocate("o1", sku, 20, repo, FakeSession())


# service-layer test:
def test_prefers_warehouse_batches_to_shipments():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(
        "in-stock-batch", "RETRO-CLOCK", 100, datetime.now(), repo, session
    )
    services.add_batch(
        "shipment-batch",
        "RETRO-CLOCK",
        100,
        datetime.now() + timedelta(days=1),
        repo,
        session,
    )

    services.allocate("oref", "RETRO-CLOCK", 10, repo, session)
    assert repo.get("in-stock-batch").available_quantity == 90
    assert repo.get("shipment-batch").available_quantity == 100


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed
