class InterExitToExitPath:
    def __init__(self, _id, key, exit1, exit2, path, eta, speed=None, length=None, congestion=None, composite=None, congestion_prediction = None, hist_eta = None ):
        self._id = _id  # MongoDB unique ID
        self.key = key  # Key for the path
        self.exit1 = exit1  # Starting exit
        self.exit2 = exit2  # Ending exit
        self.path = path  # List representing the path from exit1 to exit2
        self.eta = eta  # Estimated time of arrival or duration
        self.speed = speed  # Speed (optional)
        self.length = length  # Length (optional)
        self.congestion = congestion  # Congestion level (optional)
        self.composite = composite  # Composite value (optional)
        self.congestion_prediction = congestion_prediction
        self.hist_eta = hist_eta

    def __repr__(self):
        return f"InterExitToExitPath(exit1={self.exit1}, exit2={self.exit2}, eta={self.eta})"
