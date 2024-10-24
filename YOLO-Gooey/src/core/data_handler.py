import os
import shutil
import imagesize
import xml.etree.ElementTree as ET
from src.core.defaults import *
from sklearn.model_selection import train_test_split

class DataHandler:
    """
    A class used to encapsulate the necessary data preprocessing steps before training yolo

    """

    def __init__(self, training_data, img_paths, annotation_paths):
        self.training_data = training_data
        self.img_paths = img_paths
        self.annotation_paths = annotation_paths
        self.output_path = os.path.join(OUTPUT_TRAIN_FOLDER, os.path.basename(self.training_data))

    def prepare_data(self):
        """ Prepares the training data folder and necessary files required to train yolo

        """
        self.create_train_folder()
        self.generate_YOLO_data()
        self.create_train_val_split()
        self.create_data_yaml_folder()


    def create_train_folder(self):
        """ Create directory that contains the training data

        """
        os.makedirs(self.output_path, exist_ok=True)


    def generate_YOLO_data(self):
        """ Transforms PascalVOC annotations into yolo and copies them into the training dataset folder

        """
        self.classes = self.crawl_classes_from_annotations()
        self.create_data_folder()


    def crawl_classes_from_annotations(self):
        """ Crawl all the annotation files to extract the set of classes

        This is necessary in order to assign class indexes to yolo annotations.

        Returns
        -------
        list[str]
            a list of the crawled classes sorted lexicographically

        """
        def get_classes_from_xml_file(file):
            file_classes = set()
            root = ET.parse(file).getroot()
            for node in root:
                if node.tag == 'object':
                    for child_node in node:
                        if child_node.tag == 'name':
                            file_classes.add(child_node.text)
            return file_classes
        classes = set()
        for annotation_xml in self.annotation_paths:
            file_classes = get_classes_from_xml_file(annotation_xml)
            classes = classes.union(file_classes)
        return sorted(list(classes))

    
    def pascal_voc_to_yolo(self, img, annotation):
        """ Converts PascalVOC annotations into the yolo format

        The yolo format consists of 5 entries:
        <class_idx> <x_center> <y_center> <width> <height>

        Note that the coordinates and sizes are normalized by the image height or width
        to lie in the [0, 1] interval.

        Parameters
        ----------
        img : str
            path to image file
        annotation: str
            path to annotation file

        Returns
        -------
        list[str]
            a list of string yolo annotations found in the original PascalVOC annotation file.

        """
        width, height = imagesize.get(img)
        root = ET.parse(annotation).getroot()
        yolo_lines = []
        for node in root:
            if node.tag == 'object':
                object_line = []
                for child_node in node:
                    if child_node.tag == 'name':
                        object_line += [str(self.classes.index(child_node.text))]
                    elif child_node.tag == 'bndbox':
                        bndbox = {}
                        for coord_node in child_node:
                            bndbox[coord_node.tag] = coord_node.text
                        xmin = int(bndbox['xmin'])
                        xmax = int(bndbox['xmax'])
                        ymin = int(bndbox['ymin'])
                        ymax = int(bndbox['ymax'])
                        object_line += [str(round(0.5*(xmax+xmin)/width, DECIMAL_PRECISION))]
                        object_line += [str(round(0.5*(ymax+ymin)/height, DECIMAL_PRECISION))]
                        object_line += [str(round((xmax - xmin)/width, DECIMAL_PRECISION))]
                        object_line += [str(round((ymax - ymin)/height, DECIMAL_PRECISION))]
                yolo_lines += [' '.join(object_line) + '\n']
        return yolo_lines


    def create_data_folder(self):
        """ Create data directory that contains training images and yolo annotations

        The original training images are copies into the data directory. The original PascalVOC
        annotations are transformed into the yolo format and then copies into the data directory.

        """
        data_path_images = os.path.join(self.output_path, DATA_FOLDER, IMAGES_FOLDER)
        data_path_labels = os.path.join(self.output_path, DATA_FOLDER, LABELS_FOLDER)
        os.makedirs(data_path_images, exist_ok=True)
        os.makedirs(data_path_labels, exist_ok=True)
        for img, annotation in zip(self.img_paths, self.annotation_paths):
            shutil.copy(img, data_path_images)
            yolo_lines = self.pascal_voc_to_yolo(img, annotation)
            yolo_annotation_path = os.path.join(data_path_labels, os.path.splitext(os.path.basename(annotation))[0] + '.txt')
            with open(yolo_annotation_path, 'w') as f:
                f.writelines(yolo_lines)


    def create_train_val_split(self):
        """ Returns minimum of size and height of images in the training dataset

        This functions is required to calculate the new image size when training yolo.

        """
        full_img_paths = list(map(lambda x: os.path.join(self.output_path, DATA_FOLDER, IMAGES_FOLDER, os.path.basename(x)), self.img_paths))
        train_subset, val_subset = train_test_split(full_img_paths, train_size=TRAIN_VAL_RATIO)
        with open(os.path.join(self.output_path, DATA_FOLDER, TRAIN_FILE), 'w') as f:
            f.writelines('\n'.join(train_subset))
        with open(os.path.join(self.output_path, DATA_FOLDER, VAL_FILE), 'w') as f:
            f.writelines('\n'.join(val_subset))


    def create_data_yaml_folder(self):
        """ Creates dataset.yaml folder required for training yolo

        The dataset.yaml file contains metadata about the training dataset including
        the paths to the training images, the training/validation splits and the object
         classes crawled from the annotations.

        """
        self.dataset_yaml_path = os.path.join(self.output_path, DATA_FOLDER, DATASET_YAML_FILE)
        path = os.path.join('..', self.output_path, DATA_FOLDER)
        with open(self.dataset_yaml_path, 'w') as f:
            f.write(f'path: {path}\n')
            f.write(f'train: {TRAIN_FILE}\n')
            f.write(f'val: {VAL_FILE}\n')
            f.write(f'nc: {len(self.classes)}\n')
            classes_string = ', '.join(list(map(lambda x: '\''+x+'\'', self.classes)))
            f.write(f'names: [{classes_string}]\n')

    
    def get_image_size(self):
        """ Returns minimum of width and height of images in the training dataset

        This functions is required to calculate the new image size when training yolo.

        Returns
        -------
        int
            the minimum of width and height of images in the training dataset

        """
        width, height = imagesize.get(self.img_paths[0])
        return min(width, height)