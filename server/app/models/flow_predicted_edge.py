class FlowPredictedEdge:
    def __init__(self, _id, prediction_0, prediction_10, prediction_20, prediction_30, prediction_40, prediction_50, junction1, junction2):
        self._id = _id  # MongoDB unique ID
        self.prediction_0 = prediction_0
        self.prediction_10 = prediction_10
        self.prediction_20 = prediction_20
        self.prediction_30 = prediction_30
        self.prediction_40 = prediction_40
        self.prediction_50 = prediction_50
        self.junction1 = junction1
        self.junction2 = junction2


