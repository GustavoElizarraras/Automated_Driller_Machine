import cv2
import numpy as np
pcb1 = cv2.imread('dataset/hand_picked_originals/12000068_test.jpg')
pcb1_bin = cv2.bitwise_not(cv2.imread('dataset/hand_picked_originals/12000068_test.jpg', 0))

grosor=1
fuente=cv2.FONT_HERSHEY_COMPLEX

# ret,pcb1 = cv2.threshold(pcb1, 127, 255,cv2.THRESH_BINARY)

cv2.imshow("img00", pcb1_bin)
cv2.waitKey(0)
# morph_erosion = cv2.erode(pcb1, (15,15),iterations = 1)
kernel = np.ones((3,3),np.uint8)
pcb1_bin = cv2.erode(pcb1_bin, kernel,iterations = 1)

cv2.imshow("img0", pcb1_bin)
cv2.waitKey(0)
cv2.imshow("img0", cv2.bitwise_not(pcb1_bin))
cv2.waitKey(0)
# 120 images: param2 = 9, minRadius = 7, maxRadius = 9
# 121 images: param2 = 15, minRadius = 8, maxRadius = 23, kernel= (3,3)
# 123 images: param2 = 14, minRadius = 12, maxRadius = 23. kernel = (7,7)
# 130 images: param2 = 13, minRadius = 8, maxRadius = 24, kernel = (3,3)
# 901 images: param2 = 13, minRadius = 8, maxRadius = 20
# 920 images: param2 = 11, minRadius = 5, maxRadius = 10, kernel = (7,7)
detected_circles = cv2.HoughCircles(pcb1_bin, 
                   cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
               param2 = 9, minRadius = 7, maxRadius = 9)

for pt in detected_circles[0, :]:
    # circle coords
    a, b, r = int(pt[0]), int(pt[1]), int(pt[2])
    r2 = int(1.1*r)
    cv2.circle(pcb1, (a, b), r2, (255, 255, 255), -1)

    # Draw the circumference of the circle.
    cv2.circle(pcb1, (a, b), r, (0, 255, 0), 2)

    # Draw a small circle (of radius 1) to show the center.
    # cv2.circle(pcb1, (a, b), 1, (0, 0, 255), 3)

cv2.imshow("circles", pcb1)
cv2.waitKey(0)