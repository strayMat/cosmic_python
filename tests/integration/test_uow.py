import pytest
from sqlalchemy import text

import cosmic_python.domain.model as model
import cosmic_python.service_layer.services as services
import cosmic_python.service_layer.unit_of_work as unit_of_work
from cosmic_python.adapters.repository import FakeRepository


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])  # (1)
        self.committed = False  # (2)

    def commit(self):
        self.committed = True  # (2)

    def rollback(self):
        pass


# Mock SQL queries
def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:ref, :sku, :qty, :eta)"
        ),
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(  # (1)
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = session.execute(  # (1)
        text(
            "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
            " WHERE orderline_id=:orderlineid"
        ),
        dict(orderlineid=orderlineid),
    )
    return batchref


def test_add_batch():
    uow = FakeUnitOfWork()  # (3)
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)  # (3)
    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()  # (3)
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, uow)  # (3)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)  # (3)
    assert result == "batch1"


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session, "batch1", "HIPSTER-WORKBENCH", 100, None)
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)  # (1)
    with uow:
        batch = uow.batches.get(reference="batch1")  # (2)
        line = model.OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        batch.allocate(line)
        uow.commit()  # (3)

    batchref = get_allocated_batch_ref(session, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []
