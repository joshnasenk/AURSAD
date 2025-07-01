import numpy as np

class ModelAggregator:
    def __init__(self):
        self.coefs = []
        self.intercepts = []

    def add_weights(self, coef, intercept):
        self.coefs.append(np.array(coef))
        self.intercepts.append(np.array(intercept))

    def aggregate(self):
        avg_coef = np.mean(self.coefs, axis=0).tolist()
        avg_intercept = np.mean(self.intercepts, axis=0).tolist()
        return avg_coef, avg_intercept