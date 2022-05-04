import cv2
import numpy as np
import string
import random

def generate_random_ascii():
    char = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(random.choice(char))

def generate_random_font_type():
    combinations = {
        1: {"size": 0.9, "font": cv2.FONT_HERSHEY_COMPLEX, "org": (0,17), "thick": 1},
        2: {"size": 1.5, "font": cv2.FONT_HERSHEY_COMPLEX, "org": (0,29), "thick": 2},
        3: {"size": 1.25, "font": cv2.FONT_HERSHEY_DUPLEX, "org": (0,26), "thick": 1},
        4: {"size": 1.25, "font": cv2.FONT_HERSHEY_TRIPLEX, "org": (0,26), "thick": 1},
        5: {"size": 1.25, "font": cv2.FONT_HERSHEY_TRIPLEX, "org": (0,26), "thick": 2},
    }
    rand_int = random.randint(1, 5)
    return combinations[rand_int]

def cv2_ascii(font, font_size, thick, coords):
    text = generate_random_ascii()
    (text_width, text_height) = cv2.getTextSize(text, font, font_size, thick)[0]
    mask = np.zeros((text_height, text_width), dtype=np.uint8)
    mask = cv2.putText(mask, text, coords, font, font_size, font_color, thick, cv2.LINE_AA)
    mask = cv2.resize(mask, (30, 30), interpolation=cv2.INTER_AREA)
    mask = cv2.bitwise_not(cv2.merge((mask, mask, mask)))
    return mask

if __name__ == "__main__":
    # random type of font
    font_combination = generate_random_font_type()
    font = font_combination["font"]
    font_size = font_combination["size"]
    thick = font_combination["thick"]
    coords = font_combination["org"]
    font_color = (255, 255, 255)
    # image processing
    x_start, y_start = 5, 5
    rotations = [None, cv2.ROTATE_90_CLOCKWISE, 
                          cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180]
    for k, rotation in enumerate(rotations):
        # reading images
        pcb1 = cv2.imread('dataset/hand_picked/12000001_original.jpg')
        pcb1_bin = cv2.bitwise_not(cv2.imread('dataset/hand_picked/12000001_original.jpg', 0))
        for j in range(21):
            for i in range (21):
                sub_image = cv2.bitwise_not(pcb1[x_start:x_start + 30, y_start:y_start + 30, :]) / 255
                blackness = np.sum(sub_image)
                if blackness < 90:
                    ascii_mask = cv2_ascii(font, font_size, thick, coords)
                    if rotation is not None:
                        ascii_mask = cv2.rotate(ascii_mask, rotation)
                    pcb1[x_start:x_start + 30, y_start:y_start + 30, :] = ascii_mask
                x_start += 30
                if i == 20:
                    x_start = 5
            y_start += 30
            if j == 20:
                y_start = 5
    
        cv2.imshow("img", pcb1)
        cv2.waitKey(0)