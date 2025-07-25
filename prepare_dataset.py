import pandas as pd

df = pd.read_csv("original.csv")  # 🔁 Replace with your actual filename

# ✅ Rename to match the Flask app expectations
df.rename(columns={
    "estimated_diameter_min": "diameter_min",
    "relative_velocity": "relative_velocity",
    "miss_distance": "miss_distance",
    "is_hazardous": "hazardous"
}, inplace=True)

# ✅ Convert boolean to string for Plotly compatibility
df["hazardous"] = df["hazardous"].astype(str)

# Optional: filter out bad data
df = df[df["diameter_min"] > 0]
df = df[df["relative_velocity"] > 0]
df = df[df["miss_distance"] > 0]

# ✅ Save it with correct name used in your app
df.to_csv("nearest-earth-objects.csv", index=False)

print("✅ Cleaned file saved as: nearest-earth-objects.csv")
