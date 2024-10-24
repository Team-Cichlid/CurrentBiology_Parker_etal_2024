import argparse
import os
import xmltodict
import shutil
import cv2
import numpy as np
import math

from glob import glob
from time import time
from random import randint, uniform, sample


def augment_detector_data(path):
    '''
    You can enable/disable specific augmentations by (un)commenting them.
    '''
    files = sorted(os.listdir(path))
    imgs, annotations = files[::2], files[1::2]
    for img, anot in zip(imgs, annotations):
        img_path = os.path.join(path, img)
        anot_path = os.path.join(path, anot)
        rotate_img(img_path, 90)
        rotate_bbox(anot_path, 90)
        rotate_img(img_path, 180)
        rotate_bbox(anot_path, 180)
        rotate_img(img_path, 270)
        rotate_bbox(anot_path, 270)
        brighten_img(img_path)
        brighten_bbox(anot_path)
        blur_img(img_path)
        blur_bbox(anot_path)
        contrast_img(img_path)
        contrast_bbox(anot_path)
        sharpen_img(img_path)
        sharpen_bbox(anot_path)
    return


def augment_classifier_data(path):
    for img_class in os.listdir(path):
        class_path = os.path.join(path, img_class)
        for img in os.listdir(class_path):
            img_path = os.path.join(class_path, img)
            rotate_img(img_path, 90)
            rotate_img(img_path, 180)
            rotate_img(img_path, 270)
            brighten_img(img_path)
            blur_img(img_path)
            contrast_img(img_path)
            sharpen_img(img_path)
    return


IMG_FORMATS = ['.jpg', '.jpeg', '.png']
SHARPEN_KERNEL = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
ROTATION_FLAGS = {90: cv2.ROTATE_90_COUNTERCLOCKWISE,
                  180: cv2.ROTATE_180,
                  270: cv2.ROTATE_90_CLOCKWISE}


#######################################################################
#######################################################################
#######################################################################

def get_data_path():
    parser = argparse.ArgumentParser(
        description='Perform data augmentation for classifier/detector data.')
    parser.add_argument('--data', '-d', help='path to data folder.', required=True)
    inputs = parser.parse_args()
    return inputs.data


def backup_warning():
    print('-' * 20)
    print('Please make sure your data is backed up.')
    answer = input('Proceed ? [y/n] ')
    if not answer.lower() in ['y', 'yes']:
        print('aborting')
        exit(-1)
    print('Augmenting Data ...')
    return


def is_classifier_data(path):
    files = [x for x in os.listdir(
        path) if os.path.isfile(os.path.join(path, x))]
    directories = [x for x in os.listdir(
        path) if os.path.isdir(os.path.join(path, x))]
    for dir in directories:
        dir_path = os.path.join(path, dir)
        for file in os.listdir(dir_path):
            if not os.path.splitext(file)[-1] in IMG_FORMATS:
                return False
    return len(files) == 0 and len(directories) > 0


def is_detector_data(path):
    files = sorted([x for x in os.listdir(
        path) if os.path.isfile(os.path.join(path, x))])
    directories = [x for x in os.listdir(
        path) if os.path.isdir(os.path.join(path, x))]
    imgs, annotations = files[::2], files[1::2]
    formats = set(IMG_FORMATS + ['.xml'])

    if len(imgs) != len(annotations):
        print("Unequal number of annotations and images. Check your files!")
        exit(1)

    for img, annotation in zip(imgs, annotations):
        img_name, img_ext = os.path.splitext(img)
        anot_name, anot_ext = os.path.splitext(annotation)
        if img_name != anot_name or not {img_ext.lower(), anot_ext.lower()} < formats:
            return False
        
    return len(files) > 0 and len(directories) == 0


def get_data_type(path):
    if is_detector_data(path):
        print('Data type: Detector')
        return 'detector'
    elif is_classifier_data(path):
        print('Data type: Classifier')
        return 'classifier'
    print('Invalid data formats. Please check the README.md file for more help.')
    exit(-1)


def read_img(img_path):
    return cv2.imread(img_path)


def write_img(img_path, img):
    cv2.imwrite(img_path, img)
    return


def get_destination_path(src, suffix):
    file, ext = os.path.splitext(src)
    return file + '_' + suffix + ext

def add_random_noise(img, prob=0.0001):
    h, w, _ = img.shape
    n = h * w
    population = range(n)
    idxs = sample(population, int(prob * n))
    flattened = img.reshape((h*w, -1))
    flattened[idxs] = np.repeat(np.random.randint(256, size=(int(prob * n), 1)), 3, axis=1)
    img = flattened.reshape((h, w, -1))
    return img

def rotate_img(img_path, angle):
    if not angle in [90, 180, 270]:
        print('Invalid rotation angle.')
        exit(-1)
    img = read_img(img_path)
    img = add_random_noise(img)
    img = cv2.rotate(img, ROTATION_FLAGS[angle])
    write_img(get_destination_path(img_path, 'rotate_{}'.format(angle)), img)
    return


def brighten_img(img_path):
    img = read_img(img_path)
    img = add_random_noise(img)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    value = randint(1, 100)
    hsv[..., 2] = cv2.add(hsv[..., 2], value)
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    write_img(get_destination_path(img_path, 'brighten'), img)
    return


def blur_img(img_path):
    img = read_img(img_path)
    img = add_random_noise(img)
    img = cv2.medianBlur(img, ksize=7)
    write_img(get_destination_path(img_path, 'blur'), img)
    return


def contrast_img(img_path):
    img = read_img(img_path)
    img = add_random_noise(img)
    contrast = uniform(1.1, 1.8)
    img = cv2.addWeighted(img, contrast, img, 0,
                          int(round(255*(1-contrast)/2)))
    write_img(get_destination_path(img_path, 'contrast'), img)
    return


def sharpen_img(img_path):
    img = read_img(img_path)
    img = add_random_noise(img)
    img = cv2.filter2D(img, -1, SHARPEN_KERNEL)
    write_img(get_destination_path(img_path, 'sharpen'), img)
    return


def get_udict(anot_path):
    return xmltodict.parse(open(anot_path).read())


def save_new_dict(anot_path, udict):
    with open(anot_path, 'w') as f:
        f.write(xmltodict.unparse(udict, pretty=True, full_document=False))
    return


def get_correction_vector(w, h, sin, cos):
    corners = [(-w//2, h//2), (-w//2, -h//2), (w//2, -h//2), (w//2, h//2)]
    rotated_corners = []
    for c in corners:
        rotated_c = (c[0] * cos - c[1] * sin, c[0] * sin + c[1] * cos)
        rotated_corners += [rotated_c]
    xs, ys = zip(*rotated_corners)
    return np.array([min(xs), max(ys), min(xs), max(ys)])


def rotate_bbox_coordinates(bounding_box, resolution, angle):
    w, h = resolution
    bounding_box = np.array(bounding_box)
    y_inv_mask = np.array([1, -1, 1, -1])
    origin = np.array([w, h, w, h]) // 2
    bbox_shifted = (bounding_box - origin) * y_inv_mask
    radians = math.radians(angle)
    sin = math.sin(radians)
    cos = math.cos(radians)
    bbox_rotated = np.array([bbox_shifted[0] * cos - bbox_shifted[1] * sin,
                             bbox_shifted[0] * sin + bbox_shifted[1] * cos,
                             bbox_shifted[2] * cos - bbox_shifted[3] * sin,
                             bbox_shifted[2] * sin + bbox_shifted[3] * cos])
    bbox_corrected = ((
        bbox_rotated - get_correction_vector(w, h, sin, cos)) * y_inv_mask)
    xs, ys = bbox_corrected[::2], bbox_corrected[1::2]
    return np.array([min(xs), min(ys), max(xs), max(ys)]).astype(int)

def udict_rotate_bboxes(full_udict, angle):
    udict = full_udict['annotation']
    udict['filename'] = get_destination_path(
        udict['filename'], 'rotate_{}'.format(angle))
    udict['path'] = get_destination_path(
        udict['path'], 'rotate_{}'.format(angle))
    if angle in [90, 270]:
        temp = udict['size']['width']
        udict['size']['width'] = udict['size']['height']
        udict['size']['height'] = temp
    resolution = (int(udict['size']['width']), int(udict['size']['height']))
    obj_dict_list = udict['object']
    if type(obj_dict_list) != list:  # CAREFUL
        obj_dict_list = [obj_dict_list]
    for i, dct in enumerate(obj_dict_list):
        coords = dct['bndbox']
        bbox = list(
            map(int, [coords['xmin'], coords['ymin'], coords['xmax'], coords['ymax']]))
        bbox = rotate_bbox_coordinates(bbox, resolution, angle)
        coords['xmin'] = bbox[0]
        coords['ymin'] = bbox[1]
        coords['xmax'] = bbox[2]
        coords['ymax'] = bbox[3]
        obj_dict_list[i]['bndbox'] = coords
    if len(obj_dict_list) == 1:
        obj_dict_list = obj_dict_list[0]
    udict['object'] = obj_dict_list
    full_udict['annotation'] = udict
    return full_udict


def rotate_bbox(anot_path, angle):
    if not angle in [90, 180, 270]:
        print('Invlaid rotation angle.')
        exit(-1)
    udict = get_udict(anot_path)
    udict = udict_rotate_bboxes(udict, angle)
    save_new_dict(get_destination_path(
        anot_path, 'rotate_{}'.format(angle)), udict)
    return


def brighten_bbox(anot_path):
    udict = get_udict(anot_path)
    udict['annotation']['filename'] = get_destination_path(
        udict['annotation']['filename'], 'brighten')
    udict['annotation']['path'] = get_destination_path(
        udict['annotation']['path'], 'brighten')
    save_new_dict(get_destination_path(anot_path, 'brighten'), udict)
    return


def blur_bbox(anot_path):
    udict = get_udict(anot_path)
    udict['annotation']['filename'] = get_destination_path(
        udict['annotation']['filename'], 'blur')
    udict['annotation']['path'] = get_destination_path(
        udict['annotation']['path'], 'blur')
    save_new_dict(get_destination_path(anot_path, 'blur'), udict)
    return


def contrast_bbox(anot_path):
    udict = get_udict(anot_path)
    udict['annotation']['filename'] = get_destination_path(
        udict['annotation']['filename'], 'contrast')
    udict['annotation']['path'] = get_destination_path(
        udict['annotation']['path'], 'contrast')
    save_new_dict(get_destination_path(anot_path, 'contrast'), udict)
    return


def sharpen_bbox(anot_path):
    udict = get_udict(anot_path)
    udict['annotation']['filename'] = get_destination_path(
        udict['annotation']['filename'], 'sharpen')
    udict['annotation']['path'] = get_destination_path(
        udict['annotation']['path'], 'sharpen')
    save_new_dict(get_destination_path(anot_path, 'sharpen'), udict)
    return
