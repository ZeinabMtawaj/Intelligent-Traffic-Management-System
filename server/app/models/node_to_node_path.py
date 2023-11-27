class NodeToNodePath:
    def __init__(self, _id, key, node1, node2, eta, path, length, composite):
        self._id = _id  # MongoDB unique ID
        self.key = key  # Key related to the junction graph
        self.node1 = node1  # Starting node of the path
        self.node2 = node2  # Ending node of the path
        self.eta = eta  # Estimated time of arrival between the two nodes
        self.path = path  # List of nodes in the path from node1 to node2
        self.length = length
        self.composite = composite

    def __repr__(self):
        return f"NodeToNodePath(key={self.key}, from={self.node1}, to={self.node2}, eta={self.eta})"
