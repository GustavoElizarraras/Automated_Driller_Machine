import csv

with open("dataset/all_locations.csv", "r") as f:
    reader = csv.reader(f)
    first = next(reader)
    name = first[0][:8]
    positions = first[1:]
    with open("dataset/tf_locations.csv", "a") as w:
        writer = csv.writer(w)
        for row in reader:
            for img_type in ["original", "modified"]:
                name = row[0] + "_" + img_type + ".jpg"
                writer.writerow([name] + row[1:])
                for i in range(4):
                    name = row[0] + "_" + img_type + f"{i}.jpg"
                    writer.writerow([name] + row[1:])
