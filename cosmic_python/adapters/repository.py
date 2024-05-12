import abc
import cosmic_python.domain.model as model
from typing import List


class AbstractRepository(abc.ABC):
    @abc.abstractmethod  # (1)
    def add(self, batch: model.Batch):
        raise NotImplementedError  # (2)

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        self.session.add(batch)

    def get(self, reference) -> model.Batch:
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()

    def list_order_lines(self) -> List[model.OrderLine]:
        return self.session.query(model.OrderLine).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository(
            [
                model.Batch(ref, sku, qty, eta),
            ]
        )
