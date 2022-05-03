import cv2
pcb1 = cv2.imread('dataset/hand_picked/92000020_original.jpg')
pcb1_bin = cv2.bitwise_not(cv2.imread('dataset/hand_picked/92000020_original.jpg', 0))
grosor=1
fuente=cv2.FONT_HERSHEY_COMPLEX

# cv2.imshow("img1", pcb1)
# cv2.waitKey(0)
# 120 images: param1 = 50, param2 = 8, minRadius = 1, maxRadius = 6
# 121 images: param1 = 50, param2 = 13, minRadius = 7, maxRadius = 23
# 123 images: param2 = 12, minRadius = 13, maxRadius = 24
# 130 images: param2 = 13, minRadius = 8, maxRadius = 24
# 901 images: param2 = 13, minRadius = 8, maxRadius = 20
# 920 images: param2 = 11, minRadius = 5, maxRadius = 10
detected_circles = cv2.HoughCircles(pcb1_bin, 
                   cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
               param2 = 11, minRadius = 5, maxRadius = 10)

for pt in detected_circles[0, :]:
    # circle coords
    a, b, r = int(pt[0]), int(pt[1]), int(pt[2])
    r2 = int(0.62*r)
    cv2.circle(pcb1, (a, b), r2, (255, 255, 255), -1)
    # cv2.imshow("img1", pcb1)
    # cv2.waitKey(0)
    # Draw the circumference of the circle.
    cv2.circle(pcb1, (a, b), r, (0, 255, 0), 2)

    # Draw a small circle (of radius 1) to show the center.
    cv2.circle(pcb1, (a, b), 1, (0, 0, 255), 3)

cv2.imshow("img", pcb1)
cv2.waitKey(0)