from re import sub
import cv2
import numpy as np
import string
import random

def generate_random_ascii():
    char = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(char))

def cv2_ascii():
    font = cv2.FONT_HERSHEY_COMPLEX
    font_color = (255, 255, 255)
    font_size = 1.5
    thick = 1
    text = generate_random_ascii()
    (text_width, text_height) = cv2.getTextSize(text, font, font_size, thick)[0]
    mask = np.zeros((text_height, text_width), dtype=np.uint8)
    mask = cv2.putText(mask, text, (0, 30), font, font_size, font_color, thick, cv2.LINE_AA)
    mask = cv2.resize(mask, (30, 30))
    mask = cv2.bitwise_not(cv2.merge((mask, mask, mask)))
    return mask

pcb1 = cv2.imread('dataset/hand_picked/12000001_original.jpg')
pcb1_bin = cv2.bitwise_not(cv2.imread('dataset/hand_picked/12000001_original.jpg', 0))
x_start, y_start = 5, 5
for j in range(21):
    for i in range (21):
        sub_image = cv2.bitwise_not(pcb1[x_start:x_start + 30, y_start:y_start + 30, :]) / 255
        th = np.sum(sub_image)
        if th < 90:
            ascii_mask = cv2_ascii()
            pcb1[x_start:x_start + 30, y_start:y_start + 30, :] = ascii_mask
        x_start += 30
        if i == 20:
            x_start = 5
    y_start += 30
 
cv2.imshow("img", pcb1)
cv2.waitKey(0)