from myapp.app.repositories.base_repository import BaseRepository

class SegmentRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.Segment)
