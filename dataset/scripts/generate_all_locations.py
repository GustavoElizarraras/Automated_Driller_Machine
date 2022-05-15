import csv

with open("dataset/locations.txt", "r") as f:
    reader = csv.reader(f)
    first = next(reader)
    name = first[0][:8]
    positions = first[1:]
    with open("dataset/all_locations.csv", "a") as w:
        writer = csv.writer(w)
        for row in reader:
            if "original" in row[0]:
                if name == row[0][:8]:
                    positions = positions + row[1:]
                else:
                    writer.writerow([name] + positions)
                    name = row[0][:8]
                    positions = row[1:]