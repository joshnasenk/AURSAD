from sklearn.linear_model import LogisticRegression
import joblib

class LocalModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, X, y):
        self.model.fit(X, y)

    def get_weights(self):
        return self.model.coef_, self.model.intercept_

    def set_weights(self, coef, intercept):
        self.model.coef_ = coef
        self.model.intercept_ = intercept

    def save_model(self, path="client/model.joblib"):
        joblib.dump(self.model, path)
