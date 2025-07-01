import requests
from model import LocalModel

model = LocalModel()
model.load_model()

coef, intercept = model.get_weights()

response = requests.post("http://localhost:5000/upload_weights", json={
    "coef": coef,
    "intercept": intercept
})

print("Response:", response.json())
