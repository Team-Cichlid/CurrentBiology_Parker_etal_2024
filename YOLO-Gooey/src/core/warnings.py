from PyQt5.QtWidgets import QMessageBox
from src.core.defaults import *

def generic_warning(title, text, informative_text=''):
    """ Displays a message box

            Parameters
            ----------
            title : str
                Title of the message box
            text : str
                Text to describe the purpose of the message box
            informative_text : str, optional
                Additional text to display under the main text (default is '')
        """
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setInformativeText(informative_text)
    msg.exec_()

def invalid_path():
    generic_warning('Invalid Path',
                    'Training data path does not exist.')

def invalid_training_folder(minimum_num_training_data):
    generic_warning('Invalid Folder',
                    'Training data path needs to be a FOLDER containing images and annotations:',
                    f'The folder needs to contain at least {minimum_num_training_data} images ({IMG_EXTENSIONS}) and their corresponding annotations ({ANNOTATIONS_EXTENSIONS}) with the same name.')

def invalid_num_epochs():
    generic_warning('Invalid Num Epochs',
                    'Num epochs needs to be a positive integer.')

def invalid_batch_size():
    generic_warning('Invalid Batch Size',
                    'Batch size needs to be a positive integer.')

def invalid_resize_factor():
    generic_warning('Invalid Resize Factor',
                    'Resize factor needs to be a positive float.')

def invalid_video_images_path_factor():
    generic_warning('Invalid Video/Image(s) Path',
                    'Could not find video/image/images_folder.')

def invalid_video_image_file_extension():
    generic_warning('Invalid Video/Image File Extension',
                    'Only the following extensions are supported:',
                    f'-Video: {VIDEO_EXTENSIONS}\n-Image: {IMG_EXTENSIONS}')

def invalid_images_folder():
    generic_warning('Invalid Images Folder',
                    'Images folder needs to contain at least one image with the following file extensions:',
                    f'{IMG_EXTENSIONS}')

def invalid_model_folder():
    generic_warning('Invalid Model Folder',
                    'Model folder needs to have the following structure:',
                    f'modelfolder\n  |\n  |-- {TRAINED_MODEL_CONFIG}\n  |\n  |-- {TRAINED_MODEL_WEIGHTS_FOLDER}\n        |\n        |-- {TRAINED_MODEL_WEIGHTS_FILE}')

def invalid_save_folder():
    generic_warning('Invalid Save Folder',
                    f'Save folder needs to be inside yolo\'s {OUTPUT_PREDICT_FOLDER} folder (as a subfolder)')