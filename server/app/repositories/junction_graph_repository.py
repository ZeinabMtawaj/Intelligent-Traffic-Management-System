from myapp.app.repositories.base_repository import BaseRepository

class JunctionGraphRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.junction_graph)
