import cv2
import os
import random
import numpy as np
import csv

images_path = os.getcwd() + "/dataset/hand_picked_originals"
parameters = {
    "120": { "param2" :  9, "minRadius":   7, "maxRadius":  9, "kernel": (1,1) },
    "121": { "param2" : 15, "minRadius":   8, "maxRadius": 23, "kernel": (3,3) },
    "123": { "param2" : 14, "minRadius":  12, "maxRadius": 23, "kernel": (7,7) },
    "130": { "param2" : 13, "minRadius":   8, "maxRadius": 24, "kernel": (3,3) },
    "901": { "param2" : 13, "minRadius":   9, "maxRadius": 20, "kernel": (2,2) },
    "920": { "param2" : 11, "minRadius":   5, "maxRadius": 10, "kernel": (7,7) }
}
rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180]
n1 = random.randint(0,3)
for root, dir, files in os.walk(images_path):
    for image in files:
        n2 = random.randint(0,3)
        while n1 == n2:
            n2 = random.randint(0,3)
        # reading image
        image_type = image[:3]
        complete_path = "dataset/edited_images" + "/" + image_type + "/" + image

        pcb = cv2.imread(root + "/" + image)
        pcb_bin = cv2.bitwise_not(cv2.imread(root + "/" + image, 0))
        # detected circles

        pcb_erode = cv2.erode(pcb_bin, parameters[image_type]["kernel"],iterations = 1)

        if image_type == "901":
            pcb_erode = cv2.dilate(pcb_bin, parameters[image_type]["kernel"],iterations = 1)

        pcb_rotated = cv2.rotate(pcb_erode, rotations[n])

        detected_circles = cv2.HoughCircles(pcb_rotated, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
                    param2 = parameters[image_type]["param2"],
                    minRadius = parameters[image_type]["minRadius"],
                    maxRadius = parameters[image_type]["maxRadius"])
        
        locations = [image]
        saved_pcb = cv2.bitwise_not(pcb_rotated)
        try:
            for pt in detected_circles[0, :]:
                # circle coords
                a, b, r = int(pt[0]), int(pt[1]), int(pt[2])

                if image_type == "120" or image_type == "920":
                    r = int(3*r)
                    # insert a bigger white circle when a black circle is detected
                    cv2.circle(saved_pcb, (a, b), r, (255, 255, 255), -1)
                elif image_type == "901" or image_type == "121":
                    r = int(0.5*r)
                    # insert a smaller white circle when a black circle is detected
                    cv2.circle(saved_pcb, (a, b), r, (255, 255, 255), -1)
        
                cv2.imwrite(complete_path, saved_pcb)

                # writing positions to a txt file
                x1, x2 = str(a - r), str(a + r)
                y1, y2 = str(b + r), str(b - r)
                locations.append(x1)
                locations.append(y1)
                locations.append(x2)
                locations.append(y2)
            n1 = random.randint(0,3)
            with open("dataset/scrapped_locations.csv", "a") as w:
                writer = csv.writer(w)
                writer.writerow(locations)
        except:
            pass
