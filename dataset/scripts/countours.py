import cv2
pcb1 = cv2.imread('dataset/hand_picked/12100146_original.jpg')
pcb1_bin = cv2.bitwise_not(cv2.imread('dataset/hand_picked/12100146_original.jpg', 0))
grosor=1
fuente=cv2.FONT_HERSHEY_COMPLEX

# 120 images: param1 = 50, param2 = 8, minRadius = 1, maxRadius = 6
# 121 images: param1 = 50, param2 = 13, minRadius = 7, maxRadius = 23
detected_circles = cv2.HoughCircles(pcb1_bin, 
                   cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
               param2 = 13, minRadius = 7, maxRadius = 23)

for pt in detected_circles[0, :]:
    # circle coords
    a, b, r = int(pt[0]), int(pt[1]), int(pt[2])

    # Draw the circumference of the circle.
    cv2.circle(pcb1, (a, b), r, (0, 255, 0), 2)

    # Draw a small circle (of radius 1) to show the center.
    cv2.circle(pcb1, (a, b), 1, (0, 0, 255), 3)

cv2.imshow("img", pcb1)
cv2.waitKey(0)