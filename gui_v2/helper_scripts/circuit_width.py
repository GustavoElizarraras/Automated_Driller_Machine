import cv2
import numpy as np

img_array = cv2.imread("gui_v2/sujeción.jpg", 0)
img_array = img_array[0:1025, 500:1525]
image_center = tuple(np.array(img_array.shape[1::-1]) / 2)
rot_mat = cv2.getRotationMatrix2D(image_center, -2, 1.0)
img_array = cv2.warpAffine(img_array, rot_mat, img_array.shape[1::-1], flags=cv2.INTER_LINEAR)
# img_array = img_array[515:1465, 600:1550]
img_array = cv2.resize(img_array, (640, 640), interpolation= cv2.INTER_LINEAR)
cv2.imshow('bin', img_array)
cv2.waitKey(0)

_, img_array = cv2.threshold(img_array, 110 , 255, cv2.THRESH_BINARY)

# img_array = cv2.erode(img_array, (41,41),iterations = 1)

cv2.imshow('bin', img_array)
cv2.waitKey(0)
# blurred = cv2.GaussianBlur(img_array, (9, 9), 0)
# blurred = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, (29,29))
canny = cv2.Canny(img_array, 100, 255, 1)

lines_list =[]
lines = cv2.HoughLinesP(
            canny, # Input edge image
            2, # Distance resolution in pixels
            np.pi/180, # Angle resolution in radians
            threshold=200, # Min number of votes for valid line
            minLineLength=50, # Min allowed length of line
            maxLineGap=100 # Max allowed gap between line for joining them
            )

img_array =  cv2.merge([img_array, img_array, img_array])
xmax = 0
xmin = 1000
pmin, pmax = None, None
# Iterate over points
for points in lines:
      # Extracted points nested in the list
    x1,y1,x2,y2=points[0]
    if x1 < xmin:
        xmin = x1
        pmin = (xmin, y1)
    if x2 > xmax:
        xmax = x2
        pmax = (xmax, pmin[1])

print(xmax - xmin)
img_array = cv2.line(img_array, pmin, pmax, color=(255,0,0), thickness=2)


f, h = cv2.findContours(canny, cv2.RETR_TREE,  cv2.CHAIN_APPROX_SIMPLE)
canny3d = cv2.merge([canny, canny, canny])
cv2.drawContours(canny3d, f, -1, (0,255,0), 3)

cv2.imshow('bin', img_array)
cv2.waitKey(0)
# # cv2.imshow('bin', blurred)
# # cv2.waitKey(0)
# cv2.imshow('canny', canny3d)
# cv2.waitKey(0)
# print(f)