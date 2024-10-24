import os
from PyQt5 import QtWidgets as QTW
from src.core.Converted_GUIs import home_converted
from src.core.train import Train
from src.core.predict import Predict

class Home(QTW.QWidget, home_converted.Ui_Form):

    def __init__(self):
        self.app = QTW.QApplication([])
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())
        self.setWindowTitle('Gooey')

        self.annotate_button.clicked.connect(self.annotate)
        self.train_button.clicked.connect(self.train)
        self.predict_button.clicked.connect(self.predict)

    def annotate(self):
        os.system('labelImg')
    
    def train(self):
        self.train_widget = Train()
        self.train_widget.launch()

    def predict(self):
        self.predict_widget = Predict()
        self.predict_widget.launch()

    def launch(self):
        self.show()
        self.app.exec_()