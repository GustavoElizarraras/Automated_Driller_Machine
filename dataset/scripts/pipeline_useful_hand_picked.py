import cv2
import os
import numpy as np
import csv
import random

images_path = os.getcwd() + "/dataset/useful_handpicked"
gimp_path = os.getcwd() + "/dataset/useful_handpicked"
new_gimp_path = os.getcwd() + "/dataset/useful_handpicked_rot/"
rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180]
for root, dir, files in os.walk(gimp_path):
    for image in files:
        pcb = cv2.imread(gimp_path + "/" + image)
        pcb_bin = cv2.bitwise_not(cv2.imread(gimp_path + "/" + image, 0))
        # a4988
        # rotation
        for i, rotation in enumerate(rotations):
            if i == 0:
                pcb_rotated = pcb_bin
            else:
                pcb_rotated = cv2.rotate(pcb_bin, rotation)
            image_name = image[:-4] + f"_{i}" + ".jpg"
            # random erosion
            n = random. randint(0,1)
            pcb_rotated_eroded = pcb_rotated
            if n == 1:
                kernel = np.ones((3, 3),np.uint8)
                pcb_rotated_eroded = cv2.erode(pcb_rotated, kernel,iterations = 1)

            cv2.imwrite(new_gimp_path + image_name, cv2.bitwise_not(pcb_rotated_eroded))
