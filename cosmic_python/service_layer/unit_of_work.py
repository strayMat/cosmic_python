from __future__ import annotations
# necessary for the return type of the __enter__ method

import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import cosmic_python.adapters.repository as repository
import cosmic_python.config as config


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository  # (1)

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):  # (2)
        self.rollback()  # (4)

    @abc.abstractmethod
    def commit(self):  # (3)
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):  # (4)
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(  # (1)
    bind=create_engine(
        config.get_sqlite_url(),
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory  # (1)

    def __enter__(self):
        self.session = self.session_factory()  # type: Session  #(2)
        self.batches = repository.SqlAlchemyRepository(self.session)  # (2)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()  # (3)

    def commit(self):  # (4)
        self.session.commit()

    def rollback(self):  # (4)
        self.session.rollback()
