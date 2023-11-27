from pymongo.mongo_client import MongoClient
from myapp.config import MONGO_URI
from myapp.app.repositories import *


class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client.MapDb

        # Initialize repositories
        self.junction_repo = JunctionRepository(self.db)
        self.segment_repo = SegmentRepository(self.db)
        self.edge_repo = EdgeRepository(self.db)
        self.junction_graph_repo = JunctionGraphRepository(self.db)
        self.high_level_graph_repo = HighLevelGraphRepository(self.db)
        self.graph_of_junctions_repo = GraphOfJunctionsRepository(self.db)
        self.node_to_node_path_repo = NodeToNodePathRepository(self.db)
        self.node_to_exit_path_repo = NodeToExitPathRepository(self.db)
        self.inter_exit_to_exit_path_repo = InterExitToExitPathRepository(self.db)
        self.flow_predicted_edges_repo = FlowPredictedEdgeRepository(self.db)

    def ping(self):
        """Check the connection to the database."""
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(e)
