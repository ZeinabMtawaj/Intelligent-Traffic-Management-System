class NodeToExitPath:
    def __init__(self, _id, key, node1, exit_node, path, eta, length, composite):
        self._id = _id  # MongoDB unique ID
        self.key = key  # Key for the path
        self.node1 = node1  # Starting node
        self.exit_node = exit_node  # Exit node
        self.path = path  # List representing the path from node1 to exit
        self.eta = eta  # Estimated time of arrival or duration
        self.length = length
        self.composite = composite

    def __repr__(self):
        return f"NodeToExitPath(node={self.node1}, exit={self.exit_node}, eta={self.eta})"
