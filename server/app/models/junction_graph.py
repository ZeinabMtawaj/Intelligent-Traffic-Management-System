class JunctionGraph:
    def __init__(self, _id, key, directed, multigraph, nodes, links):
        self._id = _id  # MongoDB unique ID
        self.key = key  # Key for the graph
        self.directed = directed  # Whether the graph is directed or not
        self.multigraph = multigraph  # Whether the graph is a multigraph or not
        self.nodes = nodes  # List of nodes in the graph
        self.links = links  # List of links (edges) in the graph

    def __repr__(self):
        return f"JunctionGraph(key={self.key}, nodes_count={len(self.nodes)}, links_count={len(self.links)})"
