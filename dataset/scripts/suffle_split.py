import pandas as pd
max = 412
rows_names = ["file"]
for i in range(103):
    rows_names.append(f"x1_{i}")
    rows_names.append(f"y1_{i}")
    rows_names.append(f"x2_{i}")
    rows_names.append(f"y2_{i}")

df = pd.read_csv('dataset/tf_locations.csv', header=None, names=rows_names)
ds = df.sample(frac=1)
train = ds.iloc[:3750]
test = ds.iloc[3750:]

train.to_csv("dataset/train.csv", index=False)
test.to_csv("dataset/test.csv", index=False)

# with open("dataset/tf_locations.csv", "r") as r:
#     reader = csv.reader(r)
#     for row in reader:
#         if len(row) > max:
#             max = len(row)
# print(max)