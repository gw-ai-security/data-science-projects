import pandas as pd

# CSV laden
df = pd.read_csv("data/raw/sample_data.csv")

# Basis-Checks
print("Shape:")
print(df.shape)

print("\nHead:")
print(df.head(5))

print("\nMissing values:")
print(df.isna().sum())
