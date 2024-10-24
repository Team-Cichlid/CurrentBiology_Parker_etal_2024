
import os
import json
from multiprocessing import Process
#from camClass_h5 import camera_process as cam_h5
from core.camClass import camera_process as cam_avi
from core.dummy_gen import camera_process_dummy

from core.hotKeys import main
import core.setting as st

class Argos_class():
    def __init__(self, mode):
        self.processes=[]
        self.cams=[]
        self.config=None
        self.saving_mode=mode

    
    def configure_folders(self):
        config_path=os.path.join(str(os.path.dirname(os.path.realpath(__file__)) ),"settings.json" )

        with open(config_path) as config_file:
            self.config = json.load(config_file)

        if os.path.exists(os.path.join(str(os.path.dirname(os.path.realpath(__file__))),self.config["saving_folder"])) is False:
                os.mkdir(os.path.join(str(os.path.dirname(os.path.realpath(__file__))),self.config["saving_folder"]))
        
        self.config["saving_folder"]=os.path.join(str(os.path.dirname(os.path.realpath(__file__))),self.config["saving_folder"])
        
        return 

    def start(self):
        self.configure_folders()
        main(self.config, self.saving_mode)
        
        
if __name__=='__main__':
    argos=Argos_class('avi')
    argos.start()