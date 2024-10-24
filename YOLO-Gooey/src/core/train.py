import os
import re
from glob import glob
from PyQt5 import QtWidgets as QTW
from PyQt5 import QtCore as QTC
from src.core.data_handler import DataHandler
from src.core import warnings
from src.core.Converted_GUIs import train_converted
from src.yolo_wrapper import YOLOWrapper
from src.core.defaults import *

class Train(QTW.QWidget, train_converted.Ui_Form):
    """
    A class used to encapsulate yolo's training parameters

    ...
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowModality(QTC.Qt.ApplicationModal)
        self.training_data_label.adjustSize()
        self.training_data_paramters.adjustSize()

        self.training_data_button.clicked.connect(self.browse_data)
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.train_button.clicked.connect(self.train)


    def browse_data(self):
        """ Opens folder browser

        Allows user to quickly choose training data folder.

        """
        training_folder = QTW.QFileDialog.getExistingDirectory(self, 'Select training data folder:', os.getcwd(), QTW.QFileDialog.ShowDirsOnly)
        self.training_data_lineedit.setText(training_folder)


    def restore_defaults(self):
        """ Restores defaults training arguments

        Default training parameters are stored in src.GUI.defaults.py  
              
        """
        self.num_epochs_lineedit.setText(str(DEFAULT_NUM_EPOCHS))
        self.batch_size_lineedit.setText(str(DEFAULT_BATCH_SIZE))
        self.resize_factor_lineedit.setText(str(DEFAULT_RESIZE_FACTOR))


    def valid_training_data(self):
        """ Checks if training data folder is valid

        The function looks for images and their matching annotations (with the same name) in
        the data folder. A valid training data folder contains at least 10 images and annotations.
        
        Returns
        -------
        list[str]
            A list of images in the training folder which have matching annotations
        list[str]
            A list of annotations in the training folder which have matching images
        bool
            A flag to show if enough training data is available
        
        """
        training_data = self.training_data_lineedit.text()
        imgs = [os.path.join(training_data, f) for f in os.listdir(training_data) if any(f.endswith(ext) for ext in IMG_EXTENSIONS)]
        annotations = [os.path.join(training_data, f) for f in os.listdir(training_data) if any(f.endswith(ext) for ext in ANNOTATIONS_EXTENSIONS)]
        img_paths = []
        annotation_paths = []
        for img in imgs:
            for annotation in annotations:
                if os.path.splitext(img)[0] == os.path.splitext(annotation)[0]:
                    img_paths += [img]
                    annotation_paths += [annotation]
        return img_paths, annotation_paths, len(img_paths) >= MINIMUM_NUM_TRAINING_DATA


    def finished_training(self, return_code):
        """ Shows message box to indicate training process is over

        If the training was successful, a message box is displayed with the saved
        model path. Otherwise, an error is displayed with the training script's return code.

        Parameters
            ----------
            return_code : int
                Return code from running yolo's training script
                
        """
        if return_code == 0:
            title = 'Finished Training'
            text = 'Finished training. Output saved at:'
            model_folders = glob(os.path.join(self.data_handler.output_path, OUTPUT_MODEL_FOLDER+'*'))
            most_recent_model_folder = sorted(model_folders)[-1]
            informative_text = most_recent_model_folder
        else:
            title = 'Error'
            text = 'An error occured during training. Please check the terminal for more info.'
            informative_text = f'Return code: {return_code}'
        msg = QTW.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(informative_text)
        msg.exec_()


    def train(self):
        """ Checks if training parameters are valid before calling yolo wrapper class
        
        """
        positive_integer_re = '^\+?[0-9]*[1-9]+[0-9]*$'
        positive_float_re = '^\+?([0-9]*[1-9]+[0-9]*(.[0-9]*)?)|([0-9]*.[0-9]*[1-9]+[0-9]*)$'

        if not os.path.exists(self.training_data_lineedit.text()):
            warnings.invalid_path()
            return
        if not os.path.isdir(self.training_data_lineedit.text()):
            warnings.invalid_training_folder(MINIMUM_NUM_TRAINING_DATA)
            return
        img_paths, annotation_paths, enough_data = self.valid_training_data()
        if not enough_data:
            warnings.invalid_training_folder(MINIMUM_NUM_TRAINING_DATA)
            return
        if not re.match(positive_integer_re, self.num_epochs_lineedit.text()):
            warnings.invalid_num_epochs()
            return
        if not re.match(positive_integer_re, self.batch_size_lineedit.text()):
            warnings.invalid_batch_size()
            return
        if not re.match(positive_float_re, self.resize_factor_lineedit.text()):
            warnings.invalid_resize_factor()
            return

        training_data = self.training_data_lineedit.text()
        self.data_handler = DataHandler(training_data, img_paths, annotation_paths)
        self.data_handler.prepare_data()

        num_epochs = int(self.num_epochs_lineedit.text())
        batch_size = int(self.batch_size_lineedit.text())
        resize_factor = float(self.resize_factor_lineedit.text())
        img_size = int(self.data_handler.get_image_size() * resize_factor)

        yolo_wrapper = YOLOWrapper()
        return_code = yolo_wrapper.train(self.data_handler.output_path, self.data_handler.dataset_yaml_path, num_epochs, batch_size, img_size)
        self.finished_training(return_code)


    def launch(self):
        """ Displays train QWidget
        
        """
        self.show()
