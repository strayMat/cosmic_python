import cosmic_python.domain.model as model
from cosmic_python.adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    order_id: str, sku: str, qty: int, repo: AbstractRepository, session
) -> str:
    batches = repo.list()  # (1)
    if not is_valid_sku(sku, batches):  # (2)
        raise InvalidSku(f"Invalid sku {sku}")
    batchref = model.allocate(model.OrderLine(order_id, sku, qty), batches)  # (3)
    session.commit()  # (4)
    return batchref


def add_batch(
    order_id: str, sku: str, qty: int, eta, repo: AbstractRepository, session
) -> None:
    repo.add(model.Batch(order_id, sku, qty, eta))
    session.commit()
