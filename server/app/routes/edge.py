from myapp.app.db import Database
from myapp.app.routes.utils import *
from myapp.app.ai.model_loader import *
from flask import Blueprint, render_template, request, current_app, flash, jsonify, make_response, redirect, url_for
import sumolib


net = sumolib.net.readNet('/content/myapp/app/sumoFiles/newyork_city.net.xml')






edge = Blueprint('edge', __name__)

db_service = Database()









@edge.route('/update', methods=['GET'])
def update_all():
      edgeId, new_weight, type = (request.args.get(key)
                                  for key in ['edge', 'new_weight', 'type'])
      if not all([edgeId, new_weight, type]):
          return jsonify({"error": "All  must be provided"}), 400
      edge = db_service.edge_repo.get_by_item({'id': edgeId})
      first = db_service.junction_repo.get_by_item({'id': edge['from']})
      second = db_service.junction_repo.get_by_item({'id': edge['to']})
      new_weight = float(new_weight)
      modified_edge = (first, second)

      seg_u, key_u = get_segment(first['y'], first['x'])
      seg_v, key_v = get_segment(second['y'], second['x'])

      # load the graph
      JG =  nx.node_link_graph(db_service.graph_of_junctions_repo.get_by_item({}), directed= True)

      #update
      JG[first['id']][second['id']][type] = new_weight
      length =  JG[first['id']][second['id']]['length']
      congestion = JG[first['id']][second['id']]['congestion']
      speed = JG[first['id']][second['id']]['speed']
      hist_eta = JG[first['id']][second['id']]['hist_eta']
      eta = JG[first['id']][second['id']]['eta']
      congestion_prediction = JG[first['id']][second['id']]['congestion_prediction']
      if speed == 0:
        composite =float('inf')
      else:
        composite =  length + congestion + (1 / speed) + hist_eta  + congestion_prediction
      JG[first['id']][second['id']]['composite'] = composite
      db_service.graph_of_junctions_repo.replace({}, nx.node_link_data(JG))
      H = nx.node_link_graph(db_service.high_level_graph_repo.get_by_item({}), directed= True)
      inter_exit_to_exit_paths = db_service.inter_exit_to_exit_path_repo.get_all_by_item({"key": key_u })
      change_shortest(db_service.inter_exit_to_exit_path_repo, inter_exit_to_exit_paths, JG, first, second, H, "exit1", "exit2")



      if  key_u ==  key_v:
        update_shortest_paths_inside_segment( modified_edge, new_weight, seg_u, key_u, type)

      return jsonify({"res": "ok"})




@edge.route('/update_flow', methods=['GET'])
def update_flow():
  edge, flow, flow_capacity, minutes_past_hour = (request.args.get(key)
                              for key in ['edge', 'flow', 'flow_capacity', 'minutes_past_hour'])
  if not all([edge, flow, flow_capacity, minutes_past_hour]):
      return jsonify({"error": "All  must be provided"}), 400

  data = np.zeros((111, 1))
  predicted_flow = db_service.flow_predicted_edges_repo.get_all_by_item({"edge_id": edge})
  data[99 + predicted_flow["order"]] = 1
  data_transformed = scaler.transform(data)
  single_sequence_reshaped = data_transformed.reshape(1, 111, 1)

  # Predict
  prediction = flow_prediction_model.predict(single_sequence_reshaped)
  updated_value = prediction[0][99 + predicted_flow["order"]]
  y_pred = scaler.inverse_transform(updated_value)
  replaced_one =  predicted_flow
  replaced_one["prediction_"+ str(minutes_past_hour)] = flow/flow_capacity
  db_service.flow_predicted_edges_repo.replace({"order": predicted_flow["order"]}, replaced_one )







LOW_CONGESTION_THRESHOLD = 0.35
HIGH_CONGESTION_THRESHOLD = 0.75
def get_color(congestion_ratio):
    if congestion_ratio > HIGH_CONGESTION_THRESHOLD:
        return "red"
    elif LOW_CONGESTION_THRESHOLD <= congestion_ratio <= HIGH_CONGESTION_THRESHOLD:
        return "yellow"
    else:
        return "green"

@edge.route('/get_traffic_data', methods=['GET'])
def get_traffic_data():
    # with graph_of_junctions_lock:
    JG =  nx.node_link_graph(db_service.graph_of_junctions_repo.get_by_item({}), directed= True)
    edge_traffic_values = nx.get_edge_attributes(JG, 'congestion')
    traffic_data  = []
    for key, value in edge_traffic_values.items():
      item = {}
      junc1 =  db_service.junction_repo.get_by_item({'id': key[0]})
      junc2 =  db_service.junction_repo.get_by_item({'id': key[1]})
      lon1, lat1 = net.convertXY2LonLat(junc1['x'], junc1['y'])
      lon2, lat2 = net.convertXY2LonLat(junc2['x'], junc2['y'])
      item["start"] = [lat1, lon1]
      item["end"] = [lat2, lon2]
      item["traffic"] = get_color(value)
      traffic_data.append(item)
    return jsonify(traffic_data)

