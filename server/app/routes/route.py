from myapp.app.db import Database
from myapp.app.ai.model_predict import test_model
from myapp.app.routes.utils import *
from myapp.app.ai.model_loader import *
from flask import Blueprint, render_template, request, current_app, flash, jsonify, make_response, redirect, url_for
import sumolib
from datetime import datetime
from myapp.app.ai.genetic_algo import *


net = sumolib.net.readNet('/content/myapp/app/sumoFiles/newyork_city.net.xml')




routeOpt = Blueprint('route', __name__)

db_service = Database()






@routeOpt.route('/get', methods=['GET'])
def get_shortest():
  current_edge, destination_edge = (request.args.get(key)
                                   for key in ['current_edge', 'destination_edge'])

  if not all([current_edge, destination_edge]):
      return jsonify({"error": "All coordinates must be provided"}), 400
  source_junction = db_service.edge_repo.get_by_item({'id':current_edge})
  destination_junction = db_service.edge_repo.get_by_item({'id':destination_edge})
  xy_source = db_service.junction_repo.get_by_item({'id': source_junction['to']})
  xy_destination = db_service.junction_repo.get_by_item({'id': source_junction['from']})
  source_y, source_x = xy_source['y'], xy_source['x']
  destination_y, destination_x = xy_destination['y'], xy_destination['x']



  source_seg, source_key = get_segment(source_y, source_x)
  destination_seg, destination_key = get_segment(destination_y, destination_x)
  source = db_service.junction_repo.get_by_item({"y": source_y, "x": source_x})
  destination = db_service.junction_repo.get_by_item({"y": destination_y, "x": destination_x})
  if source_key == destination_key:
    node_to_node_path = db_service.node_to_node_path_repo.get_by_item({"key":source_key, "node1": source['id'], "node2": destination['id']})
    try:
      length_ = node_to_node_path['length']
      eta_ = node_to_node_path['eta']
      path_ = node_to_node_path['path']
    except:
      length_ = float('inf')
      eta_ = float('inf')
      path_ = []

  else:
    high_level_graph = nx.node_link_graph(db_service.high_level_graph_repo.get_by_item({}), directed= True)
    shortest_to_exits =db_service.node_to_exit_path_repo.get_all_by_item({"key":source_key, "node1": source['id']})
    shortest_from_exits = []
    junction_exits = destination_seg['junction_exits']
    for junction_exit in junction_exits:
       node_path = db_service.node_to_node_path_repo.get_by_item({"key":destination_key, "node1": junction_exit, "node2": destination['id'] })
       if node_path != None:
          shortest_from_exits.append(node_path)
    path_, length_, eta_, composite = get_shortest_for_points_in_different_segments(shortest_to_exits, shortest_from_exits, source['id'], destination['id'], high_level_graph)

  edge_path = []
  for i in range(len(path_)-1):
    edge = db_service.edge_repo.get_by_item({'from':path_[i],'to':path_[i+1]})['id']
    edge_path.append(edge)



  return jsonify({"path": edge_path, "length": length_, "eta": eta_})








@routeOpt.route('/get_real', methods=['GET'])
def get_shortest_real_world():

  source_junction, destination_junction = (request.args.get(key)
                                   for key in ['source_junction', 'destination_junction'])
  if not all([source_junction, destination_junction]):
      return jsonify({"error": "All coordinates must be provided"}), 400

  source_junction_lat, source_junction_lon = geocode(source_junction)
  destination_junction_lat, destination_junction_lon = geocode(destination_junction)
  source_x, source_y = net.convertLonLat2XY(source_junction_lon, source_junction_lat)
  destination_x, destination_y = net.convertLonLat2XY(destination_junction_lon, destination_junction_lat)
  source_id = get_nearest_junction( source_x, source_y)
  destination_id = get_nearest_junction( destination_x, destination_y)

  if (not source_id) or (not destination_id):
    length_ = float('inf')
    eta_ = float('inf')
    path_ = []
    return jsonify({"path": path_, "length": length_, "eta": eta_})
  source = db_service.junction_repo.get_by_item({"id": source_id})
  destination = db_service.junction_repo.get_by_item({"id": destination_id})
  source_seg, source_key = get_segment(source['y'], source['x'])
  destination_seg, destination_key = get_segment(destination['y'], destination['x'])
  if source_key == destination_key:
    node_to_node_path = db_service.node_to_node_path_repo.get_by_item({"key":source_key, "node1": source['id'], "node2": destination['id']})
    try:
      length_ = node_to_node_path['length']
      eta_ = node_to_node_path['eta']
      path_ = node_to_node_path['path']
    except:
      length_ = float('inf')
      eta_ = float('inf')
      path_ = []

  else:
    high_level_graph = nx.node_link_graph(db_service.high_level_graph_repo.get_by_item({}), directed= True)
    shortest_to_exits =  db_service.node_to_exit_path_repo.get_all_by_item({"key":source_key, "node1": source['id']})
    shortest_from_exits = []
    junction_exits = destination_seg['junction_exits']
    for junction_exit in junction_exits:
       node_path = db_service.node_to_node_path_repo.get_by_item({"key":destination_key, "node1": junction_exit, "node2": destination['id'] })
       if node_path != None:
          shortest_from_exits.append(node_path)
    path_, length_, eta_, composite = get_shortest_for_points_in_different_segments(shortest_to_exits, shortest_from_exits, source['id'], destination['id'], high_level_graph)
  edge_path = []
  if len(path_) != 0 :
      edge_path.append([source_junction_lat, source_junction_lon])
  for i in range(len(path_)):
    latlng = []
    junc = db_service.junction_repo.get_by_item({'id': path_[i]})
    y = junc['y']
    x = junc['x']
    lon, lat = net.convertXY2LonLat(x, y)
    latlng.append(lat)
    latlng.append(lon)
    edge_path.append(latlng)
  if len(path_) != 0:
      edge_path.append([destination_junction_lat, destination_junction_lon])




  return jsonify({"path": edge_path, "length": length_, "eta": eta_})












@routeOpt.route('/get_predicted_trip', methods=['GET'])
def eta_prediction():

   source_junction, destination_junction, pred_datetime = (request.args.get(key)
                                   for key in ['source_junction', 'destination_junction', 'pred_datetime'])

   if not all([source_junction, destination_junction, pred_datetime]):
        return jsonify({"error": "All coordinates must be provided"}), 400

   source_junction_lat, source_junction_lon = geocode(source_junction)
   destination_junction_lat, destination_junction_lon = geocode(destination_junction)


   source_x, source_y = net.convertLonLat2XY(source_junction_lon, source_junction_lat)
   destination_x, destination_y = net.convertLonLat2XY(destination_junction_lon, destination_junction_lat)


   source_id = get_nearest_junction( source_x, source_y)
   destination_id = get_nearest_junction( destination_x, destination_y)
   if (not source_id) or (not destination_id):
     length_ = float('inf')
     eta_ = float('inf')
     path_ = []




   junction = db_service.junction_repo.get_by_item({'id': source_id})
   dest_junction = db_service.junction_repo.get_by_item({'id': destination_id})

   dt = datetime.strptime(pred_datetime, '%Y-%m-%dT%H:%M')
   graph = nx.node_link_graph(db_service.graph_of_junctions_repo.get_by_item({}), directed= True)
   reachable_nodes = list(nx.bfs_tree(graph, source=junction['id']))
   # Extracting the subgraph
   subgraph = graph.subgraph(reachable_nodes)
   for edge in subgraph.edges:
        first = db_service.junction_repo.get_by_item({'id': edge[0]})
        second = db_service.junction_repo.get_by_item({'id': edge[1]})
        from_x = first['x']
        to_x = second['x']
        from_y = first['y']
        to_y = second['y']
        from_lon, from_lat = net.convertXY2LonLat(from_x, from_y)
        to_lon, to_lat = net.convertXY2LonLat(to_x, to_y)
        new_eta = test_model(from_lon,  to_lon, from_lat, to_lat, dt, weather_att = False, forecast = False)[0]
        graph[first['id']][second['id']]['hist_eta']= new_eta
   path = nx.shortest_path(graph, junction['id'], dest_junction['id'], weight='hist_eta')
   eta = sum(graph[path[i]][path[i + 1]]['hist_eta'] for i in range(len(path) - 1))
   length = sum(graph[path[i]][path[i + 1]]['length'] for i in range(len(path) - 1))
   edge_path = []
   if len(path) != 0 :
      edge_path.append([source_junction_lat, source_junction_lon])
   for i in range(len(path)):
      latlng = []
      junc = db_service.junction_repo.get_by_item({'id': path[i]})
      y = junc['y']
      x = junc['x']
      lon, lat = net.convertXY2LonLat(x, y)
      latlng.append(lat)
      latlng.append(lon)
      edge_path.append(latlng)
   if len(path) != 0 :
      edge_path.append([destination_junction_lat, destination_junction_lon])
   return jsonify({"path": edge_path, "eta": eta, "length": length})






@routeOpt.route('/get_shortest_multiple_routes', methods=['POST'])
def get_shortest_multiple_routes():
  INT_MAX = 2147483647
  routes = request.json['routes']
  START = 0
  nodes = []
  # print(routes)
  for route in routes[0]:
    point = {}
    junction_lat, junction_lon = geocode(route['point'])
    point['lat'] = junction_lat
    point['lon'] = junction_lon
    source_x, source_y = net.convertLonLat2XY(junction_lon, junction_lat)
    source_id = get_nearest_junction( source_x, source_y)
    if not source_id:
      length_ = float('inf')
      path_ = []

    source = db_service.junction_repo.get_by_item({"id": source_id})
    point['y'] = source['y']
    point['x'] = source['x']

    point['id'] = source_id
    nodes.append(point)


  lengths_matrix = []
  paths_matrix = []
  etas_matrix = []
  composites_matrix = []
  for node1 in nodes:
    lengths = []
    paths = []
    etas  = []
    composites = []
    for node2 in nodes:
      if node1['id'] == node2['id']:
        lengths.append(0)
        etas.append(0)
        composites.append(0)
        paths.append([])
        continue
      x1, y1 = node1['x'], node1['y']
      x2, y2 = node2['x'], node2['y']
      path, length, eta, composite = get_shortest_helper(y1, x1, y2, x2)
      if len(path) == 0:
        lengths.append(INT_MAX)
        paths.append([])
        etas.append(INT_MAX)
        composites.append(INT_MAX)
      lengths.append(length)
      paths.append(path)
      etas.append(eta)
      composites.append(composite)

    lengths_matrix.append(lengths)
    paths_matrix.append(paths)
    etas_matrix.append(etas)
    composites_matrix.append(composites)
  tsp = TSP(composites_matrix, START, 10, INT_MAX)
  places = tsp.solution.split('|')
  final_path = []
  final_length = 0
  final_eta = 0
  for i in range(len(places)-1):
    final_length += lengths_matrix[int(places[i])][int(places[i+1])]
    final_eta += etas_matrix[int(places[i])][int(places[i+1])]
    path_ = paths_matrix[int(places[i])][int(places[i+1])]
    if len(path_) != 0:
      # if i == 0:
      final_path.append([nodes[int(places[i])]['lat'], nodes[int(places[i])]['lon']])
      final_path.extend(path_)
      if i == len(places)-1:
        final_path.append([nodes[int(places[i+1])]['lat'], nodes[int(places[i+1])]['lon']])


  return jsonify({"length": final_length, "path": final_path, "eta": final_eta })





