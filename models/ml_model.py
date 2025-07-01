import numpy as np

class SimpleModel:
    def __init__(self, input_size=None):
        if input_size:
            self.weights = np.random.randn(input_size)
            self.bias = 0.0
        else:
            self.weights = None
            self.bias = None

    def train(self, X, y, lr=0.01, epochs=100):
        for _ in range(epochs):
            preds = self.predict(X)
            error = preds - y
            grad_w = X.T @ error / len(y)
            grad_b = np.mean(error)
            self.weights -= lr * grad_w
            self.bias -= lr * grad_b

    def predict(self, X):
        z = np.clip(X @ self.weights + self.bias, -500, 500)  # prevents overflow
        return 1 / (1 + np.exp(-z))

    def get_weights(self):
        return {
            "coefficients": self.weights.tolist(),
            "intercept": self.bias
        }
    
    def load_weights(self, weights_dict):
        self.weights = np.array(weights_dict["coefficients"])
        self.bias = weights_dict["intercept"]
