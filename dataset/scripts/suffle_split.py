import pandas as pd
import csv

max = 0

with open("dataset/processed_locations/all_locations.csv", "r") as r:
    reader = csv.reader(r)
    for row in reader:
        if len(row) > max:
            max = len(row)
print(max)

rows_names = ["file"]
for i in range(max//4):
    rows_names.append(f"x1_{i}")
    rows_names.append(f"y1_{i}")
    rows_names.append(f"x2_{i}")
    rows_names.append(f"y2_{i}")

df = pd.read_csv("dataset/processed_locations/all_locations.csv", header=None, names=rows_names)
ds = df.sample(frac=1)
train = ds.iloc[:310]
test = ds.iloc[310:]

train.to_csv("dataset/processed_locations/train.csv", index=False)
test.to_csv("dataset/processed_locations/test.csv", index=False)