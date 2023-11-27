from myapp.app.db import Database
from myapp.app.routes.utils import *
from myapp.app.ai.model_predict import test_model

db_service = Database()


def recalculate_eta():
    graph = nx.node_link_graph(db_service.graph_of_junctions_repo.get_by_item({}), directed= True)
    for edge in graph.edges:
            first =  db_service.junction_repo.get_by_item({'id': edge[0]})
            second =  db_service.junction_repo.get_by_item({'id': edge[1]})
            modified_edge = (first, second)
            from_x = first['x']
            to_x = second['x']
            from_y = first['y']
            to_y = second['y']
            from_lon, from_lat = net.convertXY2LonLat(from_x, from_y)
            to_lon, to_lat = net.convertXY2LonLat(to_x, to_y)
            new_eta = test_model(from_lon,  to_lon, from_lat, to_lat, datetime.now())[0]
            update_all_inside(modified_edge, new_eta, 'hist_eta')
