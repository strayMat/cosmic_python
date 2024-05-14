from datetime import datetime, timedelta

import pytest

import cosmic_python.domain.model as model
import cosmic_python.service_layer.services as services
from tests.conftest import random_sku
from tests.integration.test_uow import FakeUnitOfWork


def test_returns_allocation():
    uow = FakeUnitOfWork()
    uow.batches = uow.batches.for_batch("b1", "COMPLICATED-LAMP", 100)

    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)  # (2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    uow.batches = uow.batches.for_batch("b1", "AREALSKU", 100)  # (1)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)  # (2) (3)


def test_error_out_of_stock():
    sku = random_sku()
    uow = FakeUnitOfWork()
    uow.batches = uow.batches.for_batch("b1", sku, 10)

    with pytest.raises(model.OutOfStock, match=f"Out of stock for line {sku}"):
        services.allocate("o1", sku, 20, uow)


# service-layer test:
def test_prefers_warehouse_batches_to_shipments():
    uow = FakeUnitOfWork()
    services.add_batch("in-stock-batch", "RETRO-CLOCK", 100, datetime.now(), uow)
    services.add_batch(
        "shipment-batch", "RETRO-CLOCK", 100, datetime.now() + timedelta(days=1), uow
    )

    services.allocate("oref", "RETRO-CLOCK", 10, uow)
    assert uow.batches.get("in-stock-batch").available_quantity == 90
    assert uow.batches.get("shipment-batch").available_quantity == 100


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
