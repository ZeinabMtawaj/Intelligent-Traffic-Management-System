from myapp.app.repositories.base_repository import BaseRepository

class NodeToExitPathRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db.Node_to_exit_path)
