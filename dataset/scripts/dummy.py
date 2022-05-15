import os
import csv
import shutil

images_path = os.getcwd() + "/dataset/hand_picked"
s = set()
for root, dir, files in os.walk(images_path):
    f_set = set(files)
    with open("dataset/tf_locations.csv", "r") as r:
        reader = csv.reader(r)
        for row in reader:
            name = row[0]
            if name in files:
                s.add(name)
            else:
                print(name)
print(f_set - s)