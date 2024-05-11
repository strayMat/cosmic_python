from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import cosmic_python.config as config
import cosmic_python.model as model
import cosmic_python.orm as orm
import cosmic_python.repository as repository


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_sqlite_url()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    batches = repository.SqlAlchemyRepository(session).list()
    line = model.OrderLine(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    batchref = model.allocate(line, batches)
    session.commit()
    return {"batchref": batchref}, 201
