class Segment:
    def __init__(self, _id, junctions, junction_exits, segment_id, key):
        self._id = _id  # MongoDB unique ID
        self.junctions = junctions  # List of junctions in the segment
        self.junction_exits = junction_exits  # List of junction exits in the segment
        self.segment_id = segment_id  # Segment ID
        self.key = key  # Key for the segment

    def __repr__(self):
        return f"Segment(id={self.segment_id}, key={self.key}, junctions_count={len(self.junctions)})"
