from myapp.app.repositories.base_repository import BaseRepository

class JunctionRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.Junction)
