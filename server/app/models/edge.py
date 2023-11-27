class Edge:
    def __init__(self, _id, edge_id, start_node, end_node):
        self._id = _id  # MongoDB unique ID
        self.edge_id = edge_id  # Edge ID
        self.start_node = start_node  # Starting node of the edge
        self.end_node = end_node  # Ending node of the edge

    def __repr__(self):
        return f"Edge(id={self.edge_id}, from={self.start_node}, to={self.end_node})"
