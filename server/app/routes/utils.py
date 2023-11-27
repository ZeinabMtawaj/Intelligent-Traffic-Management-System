from myapp.app.db import Database
import math
from tenacity import retry, wait_exponential, stop_after_attempt
from geopy.geocoders import Nominatim
import sumolib
import traci
import networkx as nx


net = sumolib.net.readNet('/content/myapp/app/sumoFiles/newyork_city.net.xml')



db_service = Database()

def get_segment(y, x):
    y_index = math.floor(y / 1000)
    x_index = math.floor(x / 1000)
    # Convert the coordinates to a string to use as a key
    key = f"{y_index},{x_index}"
    segment = db_service.segment_repo.get_by_item({"key": key})
    return segment, key


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def geocode(place_name):
    geolocator = Nominatim(user_agent="RouteApp_v2.0", timeout=10)
    location = geolocator.geocode(place_name)
    if location:
        return location.latitude, location.longitude
    return None, None

def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="RouteApp_v2.0")
    location = geolocator.reverse((lat, lon))
    if location:
        return location.address
    return None

def get_nearest_junction(x, y):
  edge_id, lane_position, lane_index = traci.simulation.convertRoad(x, y)
  if not edge_id:
    return None
  is_internal = 0
  while(edge_id[0] == ":"):
    is_internal = 1
    x += 0.1
    y += 0.1
    edge_id, lane_position, lane_index = traci.simulation.convertRoad(x, y)
  edge = db_service.edge_repo.get_by_item({'id': edge_id})
  if is_internal:
    return edge["from"]
  return edge["to"]



def get_path(high_level_path):
  paths = []
  for i in range(len(high_level_path)-1):
    path =  db_service.inter_exit_to_exit_path_repo.get_by_item({"exit1": high_level_path[i], "exit2":high_level_path[i+1]})["path"]
    paths.extend(path)
  return paths





def calculate_total_length(source_to_exit_length, high_level_path, entry_to_destination_length, high_level_graph, kind):
    return source_to_exit_length + nx.path_weight(high_level_graph, high_level_path, weight=kind) + entry_to_destination_length




def get_shortest_for_points_in_different_segments(shortest_to_exits, shortest_from_exits, node_source_id, node_destination_id, high_level_graph):
  possible_paths = []
  for data in shortest_to_exits:
      source_to_exit_path = data['path']
      source_to_exit_length = data['length']
      source_to_exit_eta = data['eta']
      source_to_exit_composite = data['composite']
      high_level_source = source_to_exit_path[-1]


      for data in shortest_from_exits:
              entry_to_destination_path = data['path']
              entry_to_destination_eta = data['eta']
              entry_to_destination_length = data['length']
              entry_to_destination_composite = data['composite']
              high_level_target = entry_to_destination_path[0]

              try:

                  high_level_path = nx.shortest_path(high_level_graph, high_level_source, high_level_target, weight='composite')
                  total_length = calculate_total_length(source_to_exit_length, high_level_path, entry_to_destination_length, high_level_graph, 'length')
                  total_eta = calculate_total_length(source_to_exit_eta, high_level_path, entry_to_destination_eta, high_level_graph, 'eta')
                  total_composite = calculate_total_length(source_to_exit_composite, high_level_path, entry_to_destination_composite, high_level_graph, 'composite')
                  real_path = get_path(high_level_path)
                  full_path = source_to_exit_path[:-1] + real_path + entry_to_destination_path[1:]
                  possible_paths.append((full_path, total_length, total_eta, total_composite))
              except nx.NetworkXNoPath:
                  continue  # If there is no path in the high-level graph, we ignore this combination of exit and entry points.
  if len(possible_paths) != 0:
    # Select the path with the smallest total length
    full_path, full_length, full_eta, full_composite = min(possible_paths, key=lambda x: x[3])
  else:
    full_path = []
    full_length = float('inf')
    full_eta = float('inf')
    full_composite = float('inf')
  return full_path, full_length, full_eta, full_composite





def get_shortest_helper(source_y, source_x, destination_y, destination_x):
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
      composite = node_to_node_path['composite']
    except:
      length_ = float('inf')
      eta_ = float('inf')
      composite = float('inf')
      path_ = []

  else:
    high_level_graph = nx.node_link_graph(db_service.high_level_graph_repo.get_by_item({}), directed= True)
    shortest_to_exits = db_service.node_to_exit_path_repo.get_all_by_item({"key":source_key, "node1": source['id']})
    shortest_from_exits = []
    junction_exits = destination_seg['junction_exits']
    for junction_exit in junction_exits:
       node_path = db_service.node_to_node_path_repo.get_by_item({"key":destination_key, "node1": junction_exit, "node2": destination['id'] })
       if node_path != None:
          shortest_from_exits.append(node_path)
    path_, length_, eta_, composite = get_shortest_for_points_in_different_segments(shortest_to_exits, shortest_from_exits, source['id'], destination['id'], high_level_graph)
  edge_path = []
  for i in range(len(path_)):
    latlng = []
    junc = db_service.junction_repo.get_by_item({'id': path_[i]})
    y = junc['y']
    x = junc['x']
    lon, lat = net.convertXY2LonLat(x, y)
    latlng.append(lat)
    latlng.append(lon)
    edge_path.append(latlng)




  return edge_path, length_, eta_, composite






def change_shortest (collection, node_to_node_path, graph, first, second, change_graph, point1, point2):
  for info   in node_to_node_path:
          try:
            first_index = info["path"].index(first['id'])
            second_index = first_index +1
          except:
            continue
          if (second_index == len(info["path"]) ):
            continue
          if info["path"][second_index] == second['id']:
            try:
              node1_id = info[point1]
              node2_id = info[point2]
              info["path"] = nx.shortest_path(graph, node1_id, node2_id, weight='composite')
              path = info["path"]
              info["eta"] = sum(graph[path[i]][path[i + 1]]['eta'] for i in range(len(path) - 1))
              if (change_graph is None):
                  collection.replace_one({point1 : node1_id, point2 : node2_id}, info)
              if (change_graph is None) == False:
                change_graph.remove_edge(node1_id, node2_id)
                info["speed"] = sum(graph[path[i]][path[i + 1]]['speed'] for i in range(len(path) - 1))
                info["congestion"] = sum(graph[path[i]][path[i + 1]]['congestion'] for i in range(len(path) - 1))
                info["length"] = sum(graph[path[i]][path[i + 1]]['length'] for i in range(len(path) - 1))
                info["composite"] = sum(graph[path[i]][path[i + 1]]['composite'] for i in range(len(path) - 1))
                collection.replace_one({point1 : node1_id, point2 : node2_id}, info)
                change_graph.add_edge(node1_id, node2_id, length=info["length"], speed=info["speed"], congestion=info["congestion"], eta=  info["eta"] , composite = info["composite"])
            except Exception as e:
              pass

  if (change_graph is None) == False:
        db_service.high_level_graph_repo.replace({}, nx.node_link_data(change_graph))




def update_shortest_paths_inside_segment( modified_edge, new_weight, segment, key_u, type):
    first, second = modified_edge

    # load graph
    junction_graph =  nx.node_link_graph(db_service.junction_graph_repo.get_by_item({"key": key_u})["graph"], directed= True)

    #update
    junction_graph[first['id']][second['id']][type] = new_weight
    length =  junction_graph[first['id']][second['id']]['length']
    congestion = junction_graph[first['id']][second['id']]['congestion']
    speed = junction_graph[first['id']][second['id']]['speed']
    hist_eta = junction_graph[first['id']][second['id']]['hist_eta']
    eta = junction_graph[first['id']][second['id']]['eta']
    congestion_prediction = junction_graph[first['id']][second['id']]['congestion_prediction']
    if speed == 0:
      composite = float('inf')
    else:
      composite =  length + congestion + (1 / speed) + hist_eta  + congestion_prediction
    junction_graph[first['id']][second['id']]['composite'] = composite

    new_graph  = nx.node_link_data(junction_graph)
    new_one = {"key": key_u, "graph": new_graph}
    #save graph
    db_service.junction_graph_repo.replace({"key": key_u}, new_one)
    #load node_to_node_path[key_u]
    node_to_node_path = db_service.node_to_node_path_repo.get_all_by_item({"key":key_u})
    #update
    change_shortest(db_service.node_to_node_path_repo, node_to_node_path, junction_graph, first, second, None, "node1", "node2")
    # load node_to_exit_path[key_u]
    node_to_exit_path =db_service.node_to_exit_path_repo.get_all_by_item({"key":key_u})
    #update
    change_shortest(db_service.node_to_exit_path_repo, node_to_exit_path, junction_graph, first, second, None, "node1", "exit")





def update_all_inside(modified_edge, new_weight, type):

      first, second = modified_edge

      seg_u, key_u = get_segment(first['y'], first['x'])
      seg_v, key_v = get_segment(second['y'], second['x'])

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
      H =  nx.node_link_graph(db_service.high_level_graph_repo.get_by_item({}), directed= True)
      inter_exit_to_exit_paths =  db_service.inter_exit_to_exit_path_repo.get_all_by_item({"key": key_u })
      change_shortest(db_service.inter_exit_to_exit_path_repo, inter_exit_to_exit_paths, JG, first, second, H, "exit1", "exit2")

      if  key_u ==  key_v:
        update_shortest_paths_inside_segment( modified_edge, new_weight, seg_u, key_u, type)






