import os
import yaml
import pandas as pd
from glob import glob
from src.core.defaults import *
from src.yolo_wrapper import YOLOWrapper


class YOLOPredictHandler():

    def __init__(self, prediction_path, video_images_path, media_choice, model_folder, save_video_images, show_labels, show_conf, box_thickness):
        if prediction_path == '':
            self.prediction_path = os.path.join(OUTPUT_PREDICT_FOLDER, os.path.splitext(os.path.basename(video_images_path))[0])
        else:
            self.prediction_path = prediction_path
        os.makedirs(self.prediction_path, exist_ok=True)
        self.video_images_path = video_images_path
        self.media_choice = media_choice
        self.model_folder = model_folder
        self.save_video_images = save_video_images
        self.show_labels = show_labels
        self.show_conf = show_conf
        self.box_thickness = box_thickness

        if self.media_choice != "videos & images" and not os.path.isfile(self.video_images_path):
            extension = self.media_choice[-5:-1]
            self.video_images_path = os.path.join(self.video_images_path, '*'+extension)
        self.weights_path = os.path.join(self.model_folder, TRAINED_MODEL_WEIGHTS_FOLDER, TRAINED_MODEL_WEIGHTS_FILE)
        with open(os.path.join(self.model_folder, TRAINED_MODEL_CONFIG), 'rb') as config_file:
            self.image_size = yaml.safe_load(config_file)[CONFIG_IMGSIZE_ATTR]
        return


    def predict(self):
        yolo_wrapper = YOLOWrapper()
        yolo_predict_args = self.prediction_path, \
                            self.video_images_path, \
                            self.weights_path, self.image_size, \
                            self.save_video_images, \
                            self.show_labels, \
                            self.show_conf, \
                            self.box_thickness
        return_code = yolo_wrapper.predict(*yolo_predict_args)
        if return_code == SUCCESS_CODE_PREDICT:
            self.generate_csv_files()
        return return_code


    def get_object_classes(self):
        model_config_file_path = os.path.join(self.model_folder, TRAINED_MODEL_CONFIG)
        with open(model_config_file_path, 'rb') as model_config_file:
            dataset_yaml_path = yaml.safe_load(model_config_file)['data']
            with open(dataset_yaml_path, 'rb') as dataset_yaml:
                classes = yaml.safe_load(dataset_yaml)['names']
        return classes


    def generate_csv_files(self):
        print('-' * 20)
        print('Generating CSV files ...')
        classes = self.get_object_classes()

        def transform_yolo_line_2_table_row(file_name, file_type, line):
            frame, cls, xc, yc, w, h, conf = line.rstrip().split(' ')
            return [file_name, file_type, frame, classes[int(cls)], xc, yc, w, h, conf]

        prediction_folders= glob(os.path.join(self.prediction_path, OUTPUT_RESULT_FOLDER+'*'))
        most_recent_prediction_folder = sorted(prediction_folders)[-1]
        labels_folder = os.path.join(most_recent_prediction_folder, 'labels')
        image_txt_files = glob(os.path.join(labels_folder, 'image_*.txt'))
        video_txt_files = glob(os.path.join(labels_folder, 'video_*.txt'))
        file_mode_prefix_length = 6
        data = []
        for txt_file in image_txt_files+video_txt_files:
            base_name_no_extension = os.path.splitext(os.path.basename(txt_file))[0]
            file_name = base_name_no_extension[file_mode_prefix_length:]
            file_type = base_name_no_extension[:file_mode_prefix_length]
            with open(txt_file, 'r') as f:
                lines = f.readlines()
            lines = list(map(lambda x: transform_yolo_line_2_table_row(file_name, file_type, x), lines))
            data += lines
        df = pd.DataFrame(data, columns=['file_name',
                                    'file_type',
                                    'frame',
                                    'class',
                                    'xcenter',
                                    'ycenter',
                                    'width',
                                    'height',
                                    'confidence'])
        df.to_csv(os.path.join(labels_folder, os.path.basename(self.prediction_path) + '.csv'), index=False)
        print('Finished :)')

