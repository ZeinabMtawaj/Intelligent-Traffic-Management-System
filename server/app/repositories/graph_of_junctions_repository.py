from myapp.app.repositories.base_repository import BaseRepository

class GraphOfJunctionsRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.Graph_of_junctions)
