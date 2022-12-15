import random
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import os
from data_augmentation.bbox_util import *

lib_path = os.path.join(os.path.realpath("."), "data_aug")
sys.path.append(lib_path)


class RandomScale(object):
    """Randomly scales an image


    Bounding boxes which have an area of less than 25% in the remaining in the
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.

    Parameters
    ----------
    scale: float or tuple(float)
        if **float**, the image is scaled by a factor drawn
        randomly from a range (1 - `scale` , 1 + `scale`). If **tuple**,
        the `scale` is drawn randomly from values specified by the
        tuple

    Returns
    -------

    numpy.ndaaray
        Scaled image in the numpy format of shape `HxWxC`

    numpy.ndarray
        Tranformed bounding box co-ordinates of the format `n x 4` where n is
        number of bounding boxes and 4 represents `x1,y1,x2,y2` of the box

    """

    def __init__(self, up = True):
        self.up = up

    def __call__(self, img, bboxes):
        #Chose a random digit to scale by

        img_shape = img.shape

        scale = random.uniform()

        if self.up:
            resize_scale = 0.4 + scale
        else:
            resize_scale = 0.4 - scale

        img =  cv2.resize(img, None, fx = resize_scale, fy = resize_scale)

        bboxes[:,:4] *= [resize_scale, resize_scale, resize_scale, resize_scale]

        canvas = np.zeros(img_shape, dtype = np.uint8)

        y_lim = int(min(resize_scale, 1)*img_shape[0])
        x_lim = int(min(resize_scale, 1)*img_shape[1])


        canvas[:y_lim,:x_lim,:] =  img[:y_lim,:x_lim,:]

        img = canvas
        bboxes = clip_box(bboxes, [0,0,1 + img_shape[1], img_shape[0]], 0.20)


        return img, bboxes

class RandomTranslate(object):
    """Randomly Translates the image


    Bounding boxes which have an area of less than 25% in the remaining in the
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.

    Parameters
    ----------
    translate: float or tuple(float)
        if **float**, the image is translated by a factor drawn
        randomly from a range (1 - `translate` , 1 + `translate`). If **tuple**,
        `translate` is drawn randomly from values specified by the
        tuple

    Returns
    -------

    numpy.ndaaray
        Translated image in the numpy format of shape `HxWxC`

    numpy.ndarray
        Tranformed bounding box co-ordinates of the format `n x 4` where n is
        number of bounding boxes and 4 represents `x1,y1,x2,y2` of the box

    """

    def __init__(self, translate = 0.2, diff = False):
        self.translate = translate

        if type(self.translate) == tuple:
            assert len(self.translate) == 2, "Invalid range"
            assert self.translate[0] > 0 & self.translate[0] < 1
            assert self.translate[1] > 0 & self.translate[1] < 1


        else:
            assert self.translate > 0 and self.translate < 1
            self.translate = (-self.translate, self.translate)


        self.diff = diff

    def __call__(self, img, bboxes):

        bboxes = np.array(bboxes).reshape((-1,4))
        #Chose a random digit to scale by
        img_shape = img.shape

        #translate the image

        #percentage of the dimension of the image to translate
        translate_factor_x = random.uniform(*self.translate)
        translate_factor_y = random.uniform(*self.translate)

        if not self.diff:
            translate_factor_y = translate_factor_x

        canvas = np.zeros(img_shape).astype(np.uint8)

        corner_x = int(translate_factor_x*img.shape[1])
        corner_y = int(translate_factor_y*img.shape[0])

        #change the origin to the top-left corner of the translated box
        orig_box_cords =  [max(0,corner_y), max(corner_x,0), min(img_shape[0], corner_y + img.shape[0]), min(img_shape[1],corner_x + img.shape[1])]

        mask = img[max(-corner_y, 0):min(img.shape[0], -corner_y + img_shape[0]), max(-corner_x, 0):min(img.shape[1], -corner_x + img_shape[1]),:]
        canvas[orig_box_cords[0]:orig_box_cords[2], orig_box_cords[1]:orig_box_cords[3],:] = mask
        img = canvas

        bboxes[:,:4] += [corner_x, corner_y, corner_x, corner_y]

        bboxes = clip_box(bboxes, [0,0,img_shape[1], img_shape[0]], 0.75)

        return img, bboxes

class RandomRotate(object):
    """Randomly rotates an image


    Bounding boxes which have an area of less than 25% in the remaining in the
    transformed image is dropped. The resolution is maintained, and the remaining
    area if any is filled by black color.

    Parameters
    ----------
    angle: float or tuple(float)
        if **float**, the image is rotated by a factor drawn
        randomly from a range (-`angle`, `angle`). If **tuple**,
        the `angle` is drawn randomly from values specified by the
        tuple

    Returns
    -------

    numpy.ndaaray
        Rotated image in the numpy format of shape `HxWxC`

    numpy.ndarray
        Tranformed bounding box co-ordinates of the format `n x 4` where n is
        number of bounding boxes and 4 represents `x1,y1,x2,y2` of the box

    """

    def __init__(self, angle = 20):
        self.angle = angle

        if type(self.angle) == tuple:
            assert len(self.angle) == 2, "Invalid range"

        else:
            self.angle = (-self.angle, self.angle)

    def __call__(self, img, bboxes):

        bboxes = np.array(bboxes).reshape((-1,4))
        angle = random.uniform(*self.angle)

        w,h = img.shape[1], img.shape[0]
        cx, cy = w//2, h//2

        img = rotate_im(img, angle)

        corners = get_corners(bboxes)

        corners = np.hstack((corners, bboxes[:,4:]))


        corners[:,:8] = rotate_box(corners[:,:8], angle, cx, cy, h, w)

        new_bbox = get_enclosing_box(corners)


        scale_factor_x = img.shape[1] / w

        scale_factor_y = img.shape[0] / h

        img = cv2.resize(img, (w,h))

        new_bbox[:,:4] /= [scale_factor_x, scale_factor_y, scale_factor_x, scale_factor_y]

        bboxes  = new_bbox

        bboxes = clip_box(bboxes, [0,0,w, h], 0.75)

        return img, bboxes


class Resize(object):
    """Resize the image in accordance to `image_letter_box` function in darknet

    The aspect ratio is maintained. The longer side is resized to the input
    size of the network, while the remaining space on the shorter side is filled
    with black color. **This should be the last transform**


    Parameters
    ----------
    inp_dim : tuple(int)
        tuple containing the size to which the image will be resized.

    Returns
    -------

    numpy.ndaaray
        Sheared image in the numpy format of shape `HxWxC`

    numpy.ndarray
        Resized bounding box co-ordinates of the format `n x 4` where n is
        number of bounding boxes and 4 represents `x1,y1,x2,y2` of the box

    """

    def __init__(self, inp_dim):
        self.inp_dim = inp_dim

    def __call__(self, img, bboxes):
        w,h = img.shape[1], img.shape[0]
        img = letterbox_image(img, self.inp_dim)


        scale = min(self.inp_dim/h, self.inp_dim/w)
        bboxes[:,:4] *= (scale)

        new_w = scale*w
        new_h = scale*h
        inp_dim = self.inp_dim

        del_h = (inp_dim - new_h)/2
        del_w = (inp_dim - new_w)/2

        add_matrix = np.array([[del_w, del_h, del_w, del_h]]).astype(int)

        bboxes[:,:4] += add_matrix

        img = img.astype(np.uint8)

        return img, bboxes

class Sequence(object):

    """Initialise Sequence object

    Apply a Sequence of transformations to the images/boxes.

    Parameters
    ----------
    augemnetations : list
        List containing Transformation Objects in Sequence they are to be
        applied

    probs : int or list
        If **int**, the probability with which each of the transformation will
        be applied. If **list**, the length must be equal to *augmentations*.
        Each element of this list is the probability with which each
        corresponding transformation is applied

    Returns
    -------

    Sequence
        Sequence Object

    """
    def __init__(self, augmentations, probs = 1):


        self.augmentations = augmentations
        self.probs = probs

    def __call__(self, images, bboxes):
        for i, augmentation in enumerate(self.augmentations):
            if type(self.probs) == list:
                prob = self.probs[i]
            else:
                prob = self.probs

            if random.random() < prob:
                images, bboxes = augmentation(images, bboxes)
        return images, bboxes