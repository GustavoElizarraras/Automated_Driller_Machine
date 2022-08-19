import os
import shutil

images_path = os.getcwd() + "/dataset/"
images_dummy = os.getcwd() + "/dataset/dummy"
# images_path = os.getcwd() + "/dataset/original/PCBData"
hand_picked_set = set()
for root, dir, files in os.walk(images_dummy):
    for image in files:
        hand_picked_set.add(image[:8])

originals = os.getcwd() + "/dataset/original/PCBData"
new_path = os.getcwd() + "/dataset/hand_picked_originals/"
for root, dir, files in os.walk(originals):
    if files:
        for image in files:
            if image[:8] in hand_picked_set:
               shutil.copyfile(root + "/" + image, new_path + image)




