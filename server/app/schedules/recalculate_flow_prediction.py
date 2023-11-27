from myapp.app.db import Database
from myapp.app.routes.utils import *

db_service = Database()


def recalculate_flow_prediction(minute):
    flow_predicted_edges = db_service.flow_predicted_edges_repo.get_all_by_item({})
    for edge in flow_predicted_edges:
        first = edge["first"]
        second = edge["second"]
        modified_edge = (first, second)
        if minute + 10 > 50:
            predicting_minute = 0
        else:
            predicting_minute = minute + 10
            update_all_inside(modified_edge, edge["prediction_" + str(predicting_minute)], "congestion_prediction")
