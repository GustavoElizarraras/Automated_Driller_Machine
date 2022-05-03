import cv2
import os
import shutil

images_path = os.getcwd() + "/dataset/hand_picked"
parameters = {
    "120": { "param2" :   9, "minRadius":   1, "maxRadius":   6 },
    "121": { "param2" : 13, "minRadius":   7, "maxRadius": 23 },
    "123": { "param2" : 12, "minRadius": 13, "maxRadius": 24 },
    "130": { "param2" : 13, "minRadius":   8, "maxRadius": 24 },
    "901": { "param2" : 13, "minRadius":   8, "maxRadius": 20 },
    "920": { "param2" : 11, "minRadius":   5, "maxRadius": 10 }
}

for root, dir, files in os.walk(images_path):
    for image in files:
        # reading image
        if "original" in image:
            image_type = image[:3]
            complete_path = root + "/" + image
            modified_image_name = image.replace("original", "modified")
            pcb_3_ch = cv2.imread(complete_path)
            pcb_bin = cv2.bitwise_not(cv2.imread(complete_path, 0))
            # detected circles
            try:
                detected_circles = cv2.HoughCircles(pcb_bin, cv2.HOUGH_GRADIENT, 1, 20, param1 = 50,
                            param2 = parameters[image_type]["param2"],
                            minRadius = parameters[image_type]["minRadius"],
                            maxRadius = parameters[image_type]["maxRadius"])

                for pt in detected_circles[0, :]:
                    # circle coords
                    a, b, r = int(pt[0]), int(pt[1]), int(pt[2])
                    r2 = int(0.62*r)
                    # insert a smaller white circle when a black circle is detected
                    cv2.circle(pcb_3_ch, (a, b), r2, (255, 255, 255), -1)
                    cv2.imwrite(complete_path, pcb_3_ch)
                    # writing positions to a txt file
                    x1, x2 = str(a - r), str(a + r)
                    y1, y2 = str(b + r), str(b - r)
                    with open("dataset/locations.txt", "a") as f:
                        f.write(image + "," + x1 + "," + y1 + "," + x2 + "," + y2 + "\n")
                        f.write(modified_image_name + "," + x1 + "," + y1 + "," + x2 + "," + y2 + "\n")
            except Exception as e:
                print(image, e)
                # cv2.imshow("img", pcb_3_ch)
                # cv2.waitKey(0)