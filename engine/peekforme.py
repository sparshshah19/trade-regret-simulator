import pandas as pd 

#basically pandas is what reads a csv file
#pandas loads, cleans, inspects, transforms, and analyzes data in tables
#df means dataframe

df = pd.read_csv("dataset/raw.csv")

print("Shape", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nHead:")
print(df.head(3))

print("\nMissing % (top 10):")
print((df.isna().mean() * 100).sort_values(ascending=False).head(10))

