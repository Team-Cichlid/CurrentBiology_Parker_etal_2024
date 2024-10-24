from src.core.defaults import *

class YOLOWrapper():

    def __init__(self):
        return

    def train(self, output_path, dataset_yaml_path, num_epochs, batch_size, img_size):
        """ Calls yolo's training script via the command line

            Parameters
            ----------
            output_path : str
                Path to the project folder where the trained model will be saved
            dataset_yaml_path : str
                Path the yaml file describing the training dataset
            num_epochs : int
                Number of epochs
            batch_size : int
                Batch size
            img_size : int
                Image size

            Returns
            -------
            int
                Return code from running yolo's training script
        """
        yolo_training_command = [f'python {PATH_TRAIN}',
                                f'--epochs {num_epochs}',
                                f'--batch-size {batch_size}',
                                f'--imgsz {img_size}',
                                f'--data "{dataset_yaml_path}"',
                                f'--project "{output_path}"',
                                f'--name {OUTPUT_MODEL_FOLDER}']
        yolo_training_command = ' '.join(yolo_training_command) # + ' --weights \'output_train/fish_shell_annotations/model2/weights/best.pt\''
        return_code = os.system(yolo_training_command)
        return return_code

    def predict(self, prediction_path, data_path, weights_path, img_size, save_video_images, show_labels, show_confidence, line_thickness):
        """ Calls yolo's detection script via the command line

            Parameters
            ----------
            prediction_path : str
                Path to the project folder where the predictions will be saved
            data_path : str
                Path to video/image/images_folder to run prediction on
            weights_path : str
                Path to trained model weights
            imgsz : int
                Image size which video/image(s) will be resized to
            save_video_images : bool
                A flag to save video/image(s) with overlayed bounding boxes
            show_labels : bool
                A flag to show labels on overlayed bounding boxes
            show_confidence : bool
                A flag to show confidence on overlayed bounding boxes
            line_thickness : int
                Thickness of border lines of overlayed bounding boxes

            Returns
            -------
            int
                Return code from running yolo's detection script
        """
        yolo_predict_command = [f'python {PATH_PREDICT}',
                               f'--weights "{weights_path}"',
                               f'--source "{data_path}"',
                               f'--imgsz {img_size}',
                               f'--save-txt',
                               f'--save-conf',
                               f'--project "{prediction_path}"',
                               f'--name {OUTPUT_RESULT_FOLDER}']
        if save_video_images:
            yolo_predict_command += [f'--line-thickness {line_thickness}']
            if not show_labels:
                yolo_predict_command += [f'--hide-labels']
            if not show_confidence:
                yolo_predict_command += [f'--hide-conf']
        else:
            yolo_predict_command += ['--nosave']
        yolo_predict_command = ' '.join(yolo_predict_command)
        return_code = os.system(yolo_predict_command)
        print(f'Process ended with following return code : {return_code}')
        return return_code
