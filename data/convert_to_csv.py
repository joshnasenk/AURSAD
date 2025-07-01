import pandas as pd

print("🔍 Starting conversion...")  # ADD THIS
df = pd.read_hdf("data/AURSAD.h5", key="complete_data")
print("📊 Data loaded from .h5")  # ADD THIS

df.to_csv("data/AURSAD.csv", index=False)
print("✅ Converted to CSV successfully!")
