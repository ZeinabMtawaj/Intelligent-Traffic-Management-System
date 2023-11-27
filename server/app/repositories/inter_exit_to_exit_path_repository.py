from myapp.app.repositories.base_repository import BaseRepository

class InterExitToExitPathRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.Inter_exit_to_exit_path)
