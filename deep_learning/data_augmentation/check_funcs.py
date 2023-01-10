import numpy as np
import cv2
import random

def bbox_area(bbox):
    return (bbox[:,2] - bbox[:,0])*(bbox[:,3] - bbox[:,1])


def get_enclosing_box(corners):
    """Get an enclosing box for ratated corners of a bounding box

    Parameters
    ----------

    corners : numpy.ndarray
        Numpy array of shape `N x 8` containing N bounding boxes each described by their
        corner co-ordinates `x1 y1 x2 y2 x3 y3 x4 y4`

    Returns
    -------

    numpy.ndarray
        Numpy array containing enclosing bounding boxes of shape `N X 4` where N is the
        number of bounding boxes and the bounding boxes are represented in the
        format `x1 y1 x2 y2`

    """
    x_ = corners[:,[0,2,4,6]]
    y_ = corners[:,[1,3,5,7]]

    xmin = np.min(x_,1).reshape(-1,1)
    ymin = np.min(y_,1).reshape(-1,1)
    xmax = np.max(x_,1).reshape(-1,1)
    ymax = np.max(y_,1).reshape(-1,1)

    final = np.hstack((xmin, ymin, xmax, ymax,corners[:,8:]))

    return final.astype(float)

def rotate_im(image, angle):
    """Rotate the image.

    Rotate the image such that the rotated image is enclosed inside the tightest
    rectangle. The area not occupied by the pixels of the original image is colored
    black.

    Parameters
    ----------

    image : numpy.ndarray
        numpy image

    angle : float
        angle by which the image is to be rotated

    Returns
    -------

    numpy.ndarray
        Rotated Image

    """
    # grab the dimensions of the image and then determine the
    # centre
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    image = cv2.warpAffine(image, M, (nW, nH))

#    image = cv2.resize(image, (w,h))
    return image.astype(float)

def get_corners(bboxes):

    """Get corners of bounding boxes

    Parameters
    ----------

    bboxes: numpy.ndarray
        Numpy array containing bounding boxes of shape `N X 4` where N is the
        number of bounding boxes and the bounding boxes are represented in the
        format `x1 y1 x2 y2`

    returns
    -------

    numpy.ndarray
        Numpy array of shape `N x 8` containing N bounding boxes each described by their
        corner co-ordinates `x1 y1 x2 y2 x3 y3 x4 y4`

    """
    width = (bboxes[:,2] - bboxes[:,0]).reshape(-1,1)
    height = (bboxes[:,3] - bboxes[:,1]).reshape(-1,1)

    x1 = bboxes[:,0].reshape(-1,1)
    y1 = bboxes[:,1].reshape(-1,1)

    x2 = x1 + width
    y2 = y1

    x3 = x1
    y3 = y1 + height

    x4 = bboxes[:,2].reshape(-1,1)
    y4 = bboxes[:,3].reshape(-1,1)

    corners = np.hstack((x1,y1,x2,y2,x3,y3,x4,y4))

    return corners

def rotate_box(corners,angle,  cx, cy, h, w):

    """Rotate the bounding box.


    Parameters
    ----------

    corners : numpy.ndarray
        Numpy array of shape `N x 8` containing N bounding boxes each described by their
        corner co-ordinates `x1 y1 x2 y2 x3 y3 x4 y4`

    angle : float
        angle by which the image is to be rotated

    cx : int
        x coordinate of the center of image (about which the box will be rotated)

    cy : int
        y coordinate of the center of image (about which the box will be rotated)

    h : int
        height of the image

    w : int
        width of the image

    Returns
    -------

    numpy.ndarray
        Numpy array of shape `N x 8` containing N rotated bounding boxes each described by their
        corner co-ordinates `x1 y1 x2 y2 x3 y3 x4 y4`
    """

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

    return calculated



def draw_rect(im, cords, color = (255,0,0)):
    """Draw the rectangle on the image

    Parameters
    ----------

    im : numpy.ndarray
        numpy image

    cords: numpy.ndarray
        Numpy array containing bounding boxes of shape `N X 4` where N is the
        number of bounding boxes and the bounding boxes are represented in the
        format `x1 y1 x2 y2`

    Returns
    -------

    numpy.ndarray
        numpy image with bounding boxes drawn on it

    """

    im = im.copy()

    cords = cords[:,:4]
    cords = cords.reshape(-1,4)
    if not color:
        color = [255,255,255]
    for cord in cords:

        pt1, pt2 = (cord[0], cord[1]) , (cord[2], cord[3])

        pt1 = int(pt1[0]), int(pt1[1])
        pt2 = int(pt2[0]), int(pt2[1])

        im = cv2.rectangle(im.copy(), pt1, pt2, color, int(max(im.shape[:2])/200))
    return im

def clip_box(bbox, clip_box, alpha):
    """Clip the bounding boxes to the borders of an image

    Parameters
    ----------

    bbox: numpy.ndarray
        Numpy array containing bounding boxes of shape `N X 4` where N is the
        number of bounding boxes and the bounding boxes are represented in the
        format `x1 y1 x2 y2`

    clip_box: numpy.ndarray
        An array of shape (4,) specifying the diagonal co-ordinates of the image
        The coordinates are represented in the format `x1 y1 x2 y2`

    alpha: float
        If the fraction of a bounding box left in the image after being clipped is
        less than `alpha` the bounding box is dropped.

    Returns
    -------

    numpy.ndarray
        Numpy array containing **clipped** bounding boxes of shape `N X 4` where N is the
        number of bounding boxes left are being clipped and the bounding boxes are represented in the
        format `x1 y1 x2 y2`

    """
    bbox = np.array(bbox).reshape((-1,4))
    ar_ = (bbox_area(bbox))
    x_min = np.maximum(bbox[:,0], clip_box[0]).reshape(-1,1)
    y_min = np.maximum(bbox[:,1], clip_box[1]).reshape(-1,1)
    x_max = np.minimum(bbox[:,2], clip_box[2]).reshape(-1,1)
    y_max = np.minimum(bbox[:,3], clip_box[3]).reshape(-1,1)

    bbox = np.hstack((x_min, y_min, x_max, y_max, bbox[:,4:]))

    delta_area = ((ar_ - bbox_area(bbox))/ar_)

    mask = (delta_area < (1 - alpha)).astype(int)

    bbox = bbox[mask == 1,:]


    return bbox



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
        img = draw_rect(img, bboxes)
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

    def __init__(self, angle = 10):
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

        img = img.astype(np.uint8)

        img = cv2.resize(img, (w,h))

        new_bbox[:,:4] /= [scale_factor_x, scale_factor_y, scale_factor_x, scale_factor_y]

        bboxes  = new_bbox

        bboxes = clip_box(bboxes, [0,0,w, h], 0.75)
        img = draw_rect(img, bboxes)
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
        # new_dim = random.randint(80, 120)
        # how = random.randint(0, 1)
        # if how == 1:
        #     new_dim = -new_dim
        # self.inp_dim = img.shape[0] + new_dim

        bboxes = np.array(bboxes).reshape((-1,4)).astype(np.float64)

        w,h = img.shape[1], img.shape[0]
        a = img.copy()
        a = draw_rect(a, bboxes)
        cv2.imshow("a", a.astype(np.uint8))
        cv2.waitKey(0)
        img = letterbox_image(img, self.inp_dim)
        cv2.imshow("ff", img.astype(np.uint8))
        cv2.waitKey(0)
        scale = min(self.inp_dim/h, self.inp_dim/w)


        new_w = scale*w
        new_h = scale*h

        del_h = (self.inp_dim - new_h)/2
        del_w = (self.inp_dim - new_w)/2
        add_matrix = np.array([[del_w, del_h, del_w, del_h]]).astype(int)
        #bboxes[:,:4] += add_matrix
        print(bboxes[:,:4])
        bboxes[:,:4] *= (scale)
        print(bboxes[:,:4])
        #x = (self.inp_dim / 8) * scale
        #add_matrix = np.array([[x,x,x,x]]).astype(int)

        bboxes = bboxes.astype(int)
        print(bboxes[:,:4])

        bboxes = clip_box(bboxes, [0,0,w, h], 0.75)
        print(bboxes[:,:4])

        img = img.astype(np.uint8)
        img = draw_rect(img, bboxes)

        return img, bboxes


def letterbox_image(img, inp_dim):
    '''resize image with unchanged aspect ratio using padding

    Parameters
    ----------

    img : numpy.ndarray
        Image

    inp_dim: tuple(int)
        shape of the reszied image

    Returns
    -------

    numpy.ndarray:
        Resized image

    '''

    img_w, img_h = img.shape[1], img.shape[0]

    canvas = np.zeros((img_h, img_w, 3))
    resized_image = cv2.resize(img, (inp_dim, inp_dim ))
    new = img_h - inp_dim
    border = new // 2

    if new < 0:
        border = abs(new // 2)
        # bigger size
        canvas = resized_image[border:inp_dim-border, border:inp_dim-border]

    else:
        canvas[border:inp_dim+border, border:inp_dim+border] = resized_image

    return canvas



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

    def __init__(self):
        pass

    def __call__(self, img, bboxes):
        #Chose a random digit to scale by
        bboxes = np.array(bboxes).reshape((-1,4)).astype(np.float64)

        img_shape = img.shape

        scale = random.uniform(0.2, 0.4)
        up = random.randint(0, 1)
        if up == 1:
            resize_scale = 1 + scale
        else:
            resize_scale = 1 - scale

        img =  cv2.resize(img, None, fx = resize_scale, fy = resize_scale)

        bboxes[:,:4] *= [resize_scale, resize_scale, resize_scale, resize_scale]
        # bboxes[:,:4] *= resize_scale

        canvas = np.zeros(img_shape, dtype = np.uint8)

        y_lim = int(min(resize_scale, 1)*img_shape[0])
        x_lim = int(min(resize_scale, 1)*img_shape[1])


        canvas[:y_lim,:x_lim,:] = img[:y_lim,:x_lim,:]

        img = canvas
        bboxes = clip_box(bboxes, [0,0,1 + img_shape[1], img_shape[0]], 0.8)
        img = draw_rect(img, bboxes)

        return img, bboxes

new_boxes = []
bboxes = [137,356,151,342,137,219,151,205,183,109,197,95,274,219,288,205,273,417,289,401,91,109,105,95,529,330,545,314,137,109,151,95,530,101,544,87,92,355,104,343,90,476,106,460,45,475,59,461,47,355,59,343,413,355,425,343,412,416,426,402,530,237,544,223,183,356,197,342,320,356,334,342,46,110,60,96,320,415,334,401,530,146,544,132,230,218,242,206,367,355,379,343,530,284,544,270,308,560,318,550,230,355,242,343,275,355,287,343,366,218,378,206,184,218,196,206,530,191,544,177,46,218,58,206,412,218,424,206,321,219,333,207,308,606,318,596,365,415,379,401,93,218,105,206,152,560,162,550,273,497,285,485,153,605,163,595,183,497,195,485]
for i in range(0, len(bboxes), 4):
    x1 = bboxes[i]
    y1 = bboxes[i+1]
    x2 = bboxes[i+2]
    y2 = bboxes[i+3]
    if y1 > y2:
        y1, y2 = y2, y1
    new_boxes.append(x1)
    new_boxes.append(y1)
    new_boxes.append(x2)
    new_boxes.append(y2)
img = cv2.imread("deep_learning/data_augmentation/c22_0.jpg")

for _ in range(2):
    img_trans, bboxes_translated = Resize(500)(img, new_boxes)
    cv2.imshow("ff", img_trans)
    cv2.waitKey(0)
