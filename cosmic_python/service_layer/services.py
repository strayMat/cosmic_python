import cosmic_python.domain.model as model
from cosmic_python.adapters.repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: model.OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()  # (1)
    if not is_valid_sku(line.sku, batches):  # (2)
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)  # (3)
    session.commit()  # (4)
    return batchref
