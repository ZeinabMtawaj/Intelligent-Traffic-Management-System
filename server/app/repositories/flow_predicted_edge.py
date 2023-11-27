from myapp.app.repositories.base_repository import BaseRepository

class FlowPredictedEdgeRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.Flow_predicted_edges)
