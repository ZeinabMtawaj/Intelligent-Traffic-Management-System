from myapp.app.repositories.base_repository import BaseRepository

class EdgeRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.Edges)
