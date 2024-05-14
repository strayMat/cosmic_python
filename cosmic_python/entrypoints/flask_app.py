from datetime import datetime

from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import cosmic_python.adapters.orm as orm
import cosmic_python.adapters.repository as repository
import cosmic_python.config as config
import cosmic_python.domain.model as model
from cosmic_python.service_layer import services
from cosmic_python.service_layer.unit_of_work import SqlAlchemyUnitOfWork

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_sqlite_url()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    uow = SqlAlchemyUnitOfWork(get_session)

    try:
        batchref = services.allocate(
            request.json["orderid"], request.json["sku"], request.json["qty"], uow
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400
    return {"batchref": batchref}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    uow = SqlAlchemyUnitOfWork(get_session)
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta, uow
    )
    return "OK", 201
