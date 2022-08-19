import cv2
import os
import numpy as np
import csv
import random

images_path = os.getcwd() + "/dataset/pcb_gimp"
gimp_path = os.getcwd() + "/dataset/pcb_gimp"
new_gimp_path = os.getcwd() + "/dataset/pcb_gimp_morph/"
rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180]
for root, dir, files in os.walk(gimp_path):
    for image in files:
        pcb = cv2.imread(gimp_path + "/" + image)
        pcb_bin = cv2.bitwise_not(cv2.imread(gimp_path + "/" + image, 0))
        # random erosion
        n = random. randint(0,1)
        if n == 1:
            kernel = np.ones((3, 3),np.uint8)
            pcb_erode = cv2.erode(pcb_bin, kernel,iterations = 1)
        else:
            pcb_erode = pcb_bin
        # rotation
        for i, rotation in enumerate(rotations):
            pcb_erode = cv2.rotate(pcb_erode, rotation)
            image_name = image[:-4] + f"_{i}" + ".jpg"
            cv2.imwrite(new_gimp_path + image_name, cv2.bitwise_not(pcb_erode))
            # detected circles
            detected_circles = cv2.HoughCircles(pcb_bin, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
                                                param2 = 9, minRadius = 5, maxRadius = 11)
            locations = [image_name]
            for pt in detected_circles[0, :]:
                # circle coords
                a, b, r = int(pt[0]), int(pt[1]), int(pt[2])
                # writing positions to a txt file
                x1, x2 = str(a - r), str(a + r)
                y1, y2 = str(b + r), str(b - r)
                locations.append(x1)
                locations.append(y1)
                locations.append(x2)
                locations.append(y2)
            with open("dataset/scrapped_locations.csv", "a") as w:
                writer = csv.writer(w)
                writer.writerow(locations)