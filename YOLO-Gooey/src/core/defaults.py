import os

PATH_TRAIN = os.path.join('yolov5', 'train.py')
PATH_PREDICT = os.path.join('yolov5', 'detect.py')

# Train defaults params
IMG_EXTENSIONS = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']
VIDEO_EXTENSIONS = ['.avi', '.mp4']
ANNOTATIONS_EXTENSIONS = ['.xml']
DEFAULT_NUM_EPOCHS = 300
DEFAULT_BATCH_SIZE = 16
DEFAULT_RESIZE_FACTOR = 1
MINIMUM_NUM_TRAINING_DATA = 50

# Data handler defaults
OUTPUT_TRAIN_FOLDER = 'output_train'
OUTPUT_MODEL_FOLDER = 'model'
DATA_FOLDER = 'data'
IMAGES_FOLDER = 'images'
LABELS_FOLDER = 'labels'
TRAIN_FILE = 'train.txt'
VAL_FILE = 'val.txt'
DATASET_YAML_FILE = 'dataset.yaml'
TRAIN_VAL_RATIO = 0.8
DECIMAL_PRECISION = 5

# Predict default params
DEFAULT_LINE_THICKNESS = 3
OUTPUT_PREDICT_FOLDER = 'output_predict'
OUTPUT_RESULT_FOLDER = 'result'
TRAINED_MODEL_WEIGHTS_FOLDER = 'weights'
TRAINED_MODEL_WEIGHTS_FILE = 'best.pt'
TRAINED_MODEL_CONFIG = 'opt.yaml'
CONFIG_IMGSIZE_ATTR = 'imgsz'
SUCCESS_CODE_PREDICT = 0