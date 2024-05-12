from datetime import datetime
from sqlalchemy import text
import cosmic_python.domain.model as model
import cosmic_python.adapters.repository as repository
from tests.unit.test_04_services import FakeSession


# utils for test repository
def insert_order_line(session, order_id: str = "order1"):
    session.execute(  # (1)
        text(
            "INSERT INTO order_lines (orderid, sku, qty)"
            f' VALUES ("{order_id}", "GENERIC-SOFA", 12)'
        )
    )
    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=order_id, sku="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)'
        ),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        text('SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"'),
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id)"
            " VALUES (:orderline_id, :batch_id)"
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)  # (1)
    session.commit()  # (2)

    rows = session.execute(  # (3)
        text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session, "order1")
    batch1_id = insert_batch(session, "batch1")

    insert_allocation(session, orderline_id, batch1_id)  # (2)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference  #(3)
    assert retrieved.sku == expected.sku  # (4)
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {  # (4)
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
