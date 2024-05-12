from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cosmic_python.service_layer import services
import cosmic_python.config as config
import cosmic_python.domain.model as model
import cosmic_python.adapters.orm as orm
import cosmic_python.adapters.repository as repository


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_sqlite_url()))
app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)

    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"]
    )
    try:
        batchref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400
    return {"batchref": batchref}, 201
