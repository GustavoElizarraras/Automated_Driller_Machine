import numpy as np
import cv2
import os

def get_img_coords(coords_list):
    stacked_coords = []
    for i in range(0, len(coords_list), 4):
        x1, y1 = int(coords_list[i]), int(coords_list[i+1])
        x2, y2 = int(coords_list[i+2]), int(coords_list[i+3])
        width = (x2-x1) // 2
        height = (y1-y2) // 2

        x3 = x1
        y3 = y1 + height

        x4 = x2 + width
        y4 = y2

        # (270, _1), (180, _3), (90, _2)
        angle = 180
        rotated_corners = rotate_box(np.hstack((x1,y1,x2,y2,x3,y3,x4,y4)), angle)
        #print(rotated_corners)
        x1, y1, x2, y2, x3, y3, x4, y4 = rotated_corners[0]

        if angle == 180:
            cx = int(x1 - width)
            cy = int(y1 + height)
        elif angle == 90:
            cx = int(x1 - width)
            cy = int(y1 - height)
        elif angle == 270:
            cx = int(x1 + width)
            cy = int(y1 + height)

        stacked_coords.append(((cx, cy), abs(int((y1-y2)/2))))

    return stacked_coords


def rotate_box(corners, angle):

    cx = cy = 320
    h = w = 640

    corners = corners.reshape(-1,2)
    corners = np.hstack((corners, np.ones((corners.shape[0],1), dtype = type(corners[0][0]))))

    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)


    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cx
    M[1, 2] += (nH / 2) - cy
    # Prepare the vector to be transformed
    calculated = np.dot(M,corners.T).T

    calculated = calculated.reshape(-1,8)
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cx
    M[1, 2] += (nH / 2) - cy
    # Prepare the vector to be transformed
    calculated = np.dot(M,corners.T).T

    calculated = calculated.reshape(-1,8)

    return calculated


    return calculated

def show_green_holes(coords):
    pcb = cv2.imread(os.getcwd() + "/dataset/pcb_gimp_morph/c44_3.jpg")

    for c in coords:
        center = c[0]
        radius = c[1]
        color = (0,255,0)
        cv2.circle(pcb, center, radius, color, 4)

    return pcb

coords = [539,65,561,43,540,95,562,73,539,126,561,104,539,157,561,135,539,188,561,166,539,218,561,196,539,249,561,227,539,279,561,257,538,310,560,288,539,401,561,379,539,432,561,410,569,486,591,464,507,485,529,463,423,439,445,417,423,408,445,386,362,364,384,342,362,273,384,251,331,272,353,250,301,205,323,183,302,238,324,216,301,272,323,250,270,273,292,251,240,272,262,250,209,272,231,250,179,273,201,251,80,257,102,235,80,226,102,204,44,184,66,162,44,135,66,113,159,127,181,105,242,125,264,103,311,132,333,110,433,131,455,109,447,96,469,74,386,96,408,74,242,64,264,42,158,64,180,42,110,98,132,76,84,97,106,75,423,204,445,182,424,238,446,216,331,364,353,342,301,364,323,342,271,364,293,342,240,364,262,342,209,363,231,341,179,365,201,343,270,407,292,385,270,438,292,416,163,475,185,453,133,474,155,452,103,474,125,452,72,475,94,453,41,474,63,452,41,426,63,404,41,391,63,369,12,475,34,453,11,566,33,544,40,566,62,544,72,566,94,544,102,566,124,544,133,567,155,545,165,567,187,545,277,576,299,554,307,575,329,553,352,573,374,551,474,573,496,551]
rotated_coords = get_img_coords(coords)
img = show_green_holes(rotated_coords)
cv2.imshow("img00", img)
cv2.waitKey(0)