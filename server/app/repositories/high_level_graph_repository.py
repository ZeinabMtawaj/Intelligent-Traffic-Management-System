from myapp.app.repositories.base_repository import BaseRepository

class HighLevelGraphRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.High_level_graph)
