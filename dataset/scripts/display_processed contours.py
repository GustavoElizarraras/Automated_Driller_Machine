import cv2
import os
import numpy as np
import csv
import time

# pcb1 = cv2.imread('dataset/hand_picked/92000020_original.jpg')
# pcb1_bin = cv2.bitwise_not(cv2.imread('dataset/hand_picked/92000020_original.jpg', 0))
grosor=1
fuente=cv2.FONT_HERSHEY_COMPLEX

gimp_path = os.getcwd() + "/dataset/edited_wtypos"

with open("dataset/processed_locations/train_good.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)
    for row in reader:

        img =  os.getcwd() + "/dataset/all_good_images/" + row[0]

        pcb = cv2.imread(img)
        #centers = []
        for i in range(1, len(row), 4):
            x1, y1 = int(row[i]), int(row[i+1])
            x2, y2 = int(row[i+2]), int(row[i+3])
            half_x = (x2-x1) // 2
            half_y = (y2-y1) // 2
            #centers.append(((x2-x1)/2, (y2-y1)/2))

            cv2.circle(pcb, (x1 + half_x, y1 + half_y), int((y2-y1)/2), (0, 255, 0), 2)

        cv2.imshow(img, pcb)
        cv2.waitKey(0)
        #print(row)

# for root, dir, files in os.walk(gimp_path):
#     for image in files:
#         cb1 = cv2.imread(gimp_path + "/" + image)p
#         pcb1_bin = cv2.bitwise_not(cv2.imread(gimp_path + "/" + image, 0))

#         detected_circles = cv2.HoughCircles(pcb1_bin, cv2.HOUGH_GRADIENT, 1, 20, param1= 50,
#                                             param2 = 9, minRadius = 5, maxRadius = 11)

#         for pt in detected_circles[0, :]:
#             # circle coords
#             a, b, r = int(pt[0]), int(pt[1]), int(pt[2])
#             # Draw the circumference of the circle.
#             cv2.circle(pcb1, (a, b), r, (0, 255, 0), 2)

#             # Draw a small circle (of radius 1) to show the center.
#             cv2.circle(pcb1, (a, b), 1, (0, 0, 255), 3)

#         cv2.imshow("img", pcb1)
#         cv2.waitKey(0)