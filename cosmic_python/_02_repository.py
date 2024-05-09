from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.orm import registry

import cosmic_python._01_domain_model as model

metadata = MetaData()

order_lines = Table(  # (2)
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)


def start_mappers():
    mapper_registry = registry(metadata=metadata)
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, order_lines)  # (3)
