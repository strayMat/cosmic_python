import random
import cosmic_python.model as model
import cosmic_python.services as services
from cosmic_python.repository import FakeRepository
import pytest

from tests.conftest import random_sku


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])  # (1)

    result = services.allocate(line, repo, FakeSession())  # (2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])  # (1)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())  # (2) (3)


def test_error_out_of_stock():
    sku = random_sku()
    line = model.OrderLine("o1", sku, 20)
    batch = model.Batch("b1", sku, 10, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(model.OutOfStock, match=f"Out of stock for line {sku}"):
        services.allocate(line, repo, FakeSession())
