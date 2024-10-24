import os
import yaml
import pandas as pd
from glob import glob
from PyQt5 import QtWidgets as QTW
from PyQt5 import QtCore as QTC
from src.core import warnings
from src.core.yolo_predict_handler import YOLOPredictHandler
from src.core.Converted_GUIs import predict_converted
from src.core.defaults import *

class Predict(QTW.QWidget, predict_converted.Ui_Form):
    """
    A class used to encapsulate yolo's detection parameters

    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowModality(QTC.Qt.ApplicationModal)
        self.video_images_lineedit.adjustSize()
        self.model_folder_label.adjustSize()
        self.additional_settings_label.adjustSize()
        self.box_thickness_label.adjustSize()

        self.save_video_images_checkbox.stateChanged.connect(self.save_checkbox_state_changed)

        self.video_images_button.clicked.connect(self.browse_video_images)
        self.model_folder_button.clicked.connect(self.browse_model_folder)
        self.restore_defaults_button.clicked.connect(self.restore_defaults)
        self.help_button.clicked.connect(self.help)
        self.predict_button.clicked.connect(self.predict)


    def help(self):
        """ Displays help dialog box that explains all GUI fields for prediction

        """
        msg = QTW.QMessageBox()
        msg.setWindowTitle('Help')
        msg.setText('Input fields descriptions:')
        msg.setInformativeText('<br>'.join([
            f'<b>Video/Image(s):</b>',f'-path to 1 video, 1 image or 1 folder containing images and/or videos.<br>',
            f'<b>Model folder</b>:',f'-path to folder containing trained model. Should have a \'{TRAINED_MODEL_WEIGHTS_FOLDER}\' subfolder (\'{TRAINED_MODEL_WEIGHTS_FOLDER}/{TRAINED_MODEL_WEIGHTS_FILE}\') and config file (\'{TRAINED_MODEL_CONFIG}\').<br>',
            f'<b>save video/images with bounding boxes</b>:',f'-whether video/images should be save with overlayed bounding boxes.<br>',
            f'<b>show labels on boxes</b>:',f'-whether class labels should be shown on top of the bounding boxes.<br>',
            f'<b>show confidence on boxes</b>:',f'-whether confidence score should be shown on top of the bounding boxes.<br>',
            f'<b>box thickness</b>:',f'-controls thickness of bounding box borders. Should be an integer value between 1 and 10.<br>'
        ]))
        msg.exec_()


    def browse_video_images(self):
        """ Browse files/folders to locate video/image(s) for prediction

        In order to allow the user to choose between a file (video/image) and a folder (of images),
        a custom file/folder browser has to be used.

        """
        def updateText():
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append('"{}"'.format(index.data()))
                break
            lineEdit.setText(' '.join(selected))
        dialog = QTW.QFileDialog(self, windowTitle='Select video/image/images_folder:')
        dialog.setFileMode(dialog.ExistingFiles)
        dialog.setOption(dialog.DontUseNativeDialog, True)
        dialog.setDirectory(os.getcwd())
        dialog.setNameFilter(' '.join([f'*{ext}' for ext in IMG_EXTENSIONS+VIDEO_EXTENSIONS]))
        dialog.accept = lambda: QTW.QDialog.accept(dialog)
        stackedWidget = dialog.findChild(QTW.QStackedWidget)
        view = stackedWidget.findChild(QTW.QListView)
        view.selectionModel().selectionChanged.connect(updateText)
        lineEdit = dialog.findChild(QTW.QLineEdit)
        dialog.directoryEntered.connect(lambda: lineEdit.setText(''))
        dialog.exec_()
        file = ''
        if dialog.selectedFiles():
            file = dialog.selectedFiles()[0]
        self.video_images_lineedit.setText(file)
        default_save_path = os.path.join(OUTPUT_PREDICT_FOLDER, os.path.splitext(os.path.basename(self.video_images_lineedit.text()))[0])
        self.save_folder_lineedit.setText(default_save_path)


    def browse_model_folder(self):
        """ Browse folders to locate trained model folder

        """
        model_folder = QTW.QFileDialog.getExistingDirectory(self, 'Select trained model folder:', os.getcwd(), QTW.QFileDialog.ShowDirsOnly)
        self.model_folder_lineedit.setText(model_folder)


    def save_checkbox_state_changed(self):
        """ Function to change 'enabled' state of GUI elemented when state of 'save video/image(s)' checkbox is changed

        """
        if self.save_video_images_checkbox.isChecked():
            self.show_labels_checkbox.setEnabled(True)
            self.show_confidence_checkbox.setEnabled(True)
            self.box_thickness_spinbox.setEnabled(True)
        else:
            self.show_labels_checkbox.setEnabled(False)
            self.show_confidence_checkbox.setEnabled(False)
            self.box_thickness_spinbox.setEnabled(False)


    def restore_defaults(self):
        """ Restores defaults detection arguments

        Default training parameters are stored in src.GUI.defaults.py  

        """
        self.save_video_images_checkbox.setChecked(True)
        self.show_labels_checkbox.setChecked(True)
        self.show_confidence_checkbox.setChecked(True)
        self.box_thickness_spinbox.setValue(DEFAULT_LINE_THICKNESS)
        self.video_images_lineedit.setText('')
        self.save_folder_lineedit.setText('')
        self.model_folder_lineedit.setText('')


    def finished_prediction(self, return_code):
        """ Shows message box to indicate detection process is over

        If the detcetion was successful, a message box is displayed with the saved
        detection path. Otherwise, an error is displayed with the detection script's return code.

        Parameters
            ----------
            return_code : int
                Return code from running yolo's detection script
        """
        if return_code == 0:
            title = 'Finished Prediction'
            text = 'Finished Prediction. Output saved at:'
            informative_text = self.save_folder_lineedit.text()
            result_folders = glob(os.path.join(self.save_folder_lineedit.text(), OUTPUT_RESULT_FOLDER+'*'))
            most_recent_result_folder = sorted(result_folders)[-1]
            informative_text = most_recent_result_folder
        else:
            title = 'Error'
            text = 'An error occured during training. Please check the terminal for more info.'
            informative_text = f'Return code: {return_code}'
        msg = QTW.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setInformativeText(informative_text)
        msg.exec_()


    def predict(self):
        """ Checks if detection parameters are valid before calling yolo wrapper class

        """
        video_images_path = self.video_images_lineedit.text()
        model_folder_path = self.model_folder_lineedit.text()
        save_folder_path = self.save_folder_lineedit.text()
        self.directory_mode = False

        # Check valid video(s)/image(s) path
        if not os.path.exists(video_images_path):
            warnings.invalid_video_images_path_factor()
            return
        if os.path.isfile(self.video_images_lineedit.text()):
            if not os.path.splitext(video_images_path)[-1] in IMG_EXTENSIONS+VIDEO_EXTENSIONS:
                warnings.invalid_video_image_file_extension()
                return
            self.directory_mode = False
        else:
            images_folder_contents = os.listdir(video_images_path)
            if not any(list(map(lambda x: os.path.splitext(x)[-1] in IMG_EXTENSIONS+VIDEO_EXTENSIONS, images_folder_contents))):
                warnings.invalid_images_folder()
                return
            self.directory_mode = True

        # Check valid save folder path
        save_folder_path_split = os.path.normpath(save_folder_path).split(os.sep)
        distant_save_path = save_folder_path_split[0] != OUTPUT_PREDICT_FOLDER
        shallow_path = len(save_folder_path_split) < 2 or (len(save_folder_path_split) == 2 and save_folder_path_split[1] == '')
        if distant_save_path or shallow_path:
            warnings.invalid_save_folder()
            return

        # Check valid model path
        if not os.path.exists(model_folder_path) or not os.path.isdir(model_folder_path):
            warnings.invalid_model_folder()
            return
        model_folder_contents = os.listdir(model_folder_path)
        if not TRAINED_MODEL_CONFIG in model_folder_contents or not TRAINED_MODEL_WEIGHTS_FOLDER in model_folder_contents:
            warnings.invalid_model_folder()
            return
        model_weights_folder_path = os.path.join(model_folder_path, TRAINED_MODEL_WEIGHTS_FOLDER)
        if not os.path.isdir(model_weights_folder_path) or not TRAINED_MODEL_WEIGHTS_FILE in os.listdir(model_weights_folder_path):
            warnings.invalid_model_folder()
            return

        prediction_path = self.save_folder_lineedit.text()
        video_images_path = self.video_images_lineedit.text()
        media_choice = self.media_choice_combo_box.currentText()
        model_folder = self.model_folder_lineedit.text()
        save_video_images = self.save_video_images_checkbox.isChecked()
        show_labels = self.show_labels_checkbox.isChecked()
        show_conf = self.show_confidence_checkbox.isChecked()
        box_thickness = self.box_thickness_spinbox.value()

        self.yolo_predict_handler = YOLOPredictHandler(prediction_path, video_images_path, media_choice, model_folder, save_video_images, show_labels, show_conf, box_thickness)
        return_code = self.yolo_predict_handler.predict()
        self.finished_prediction(return_code)


    def launch(self):
        """ Displays predict QWidget

        """
        self.show()
