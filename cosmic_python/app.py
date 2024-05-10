import flask
from flask import request
from cosmic_python.orm import SqlAlchemyRepository
import cosmic_python.model as model


@flask.route.gubbins
def allocate_endpoint():
    batches = SqlAlchemyRepository.list()
    lines = [
        model.OrderLine(l["orderid"], l["sku"], l["qty"])
        for l in request.params["order_lines"]
    ]
    model.allocate(lines, batches)
    session.commit()
    return 201
