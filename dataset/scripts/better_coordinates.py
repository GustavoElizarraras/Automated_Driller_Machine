import csv

with open("dataset/processed_locations/test.csv", "r") as r:
    reader = csv.reader(r)
    next(reader)
    for row in reader:
        coords = [row[0]]
        for i in range(1, len(row), 4):
            if not row[i]:
                break
            x1 = int(float(row[i]))
            y1 = int(float(row[i+1]))
            x2 = int(float(row[i+2]))
            y2 = int(float(row[i+3]))

            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            coords.append(x1)
            coords.append(y1)
            coords.append(x2)
            coords.append(y2)
        with open("dataset/processed_locations/test_good.csv", "a") as w:
            writer = csv.writer(w)
            writer.writerow(coords)
