class Junction:
    def __init__(self, _id, junc_id, y, x):
        self._id = _id  # MongoDB unique ID
        self.junc_id = junc_id  # Junction ID
        self.y = y  # y-coordinate
        self.x = x  # x-coordinate

    def __repr__(self):
        return f"Junction(id={self.junc_id}, y={self.y}, x={self.x})"
