import cosmic_python.domain.model as model

from cosmic_python.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(order_id: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    with uow:
        batches = uow.batches.list()  # (1)
        if not is_valid_sku(sku, batches):  # (2)
            raise InvalidSku(f"Invalid sku {sku}")
        batchref = model.allocate(model.OrderLine(order_id, sku, qty), batches)  # (3)
        uow.commit()  # (4)
    return batchref


def add_batch(order_id: str, sku: str, qty: int, eta, uow: AbstractUnitOfWork) -> None:
    with uow:
        uow.batches.add(model.Batch(order_id, sku, qty, eta))
        uow.commit()
