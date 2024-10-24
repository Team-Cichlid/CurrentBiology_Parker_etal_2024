import sys
import os

from multiprocessing import Process
import multiprocessing

from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMainWindow, QMessageBox, QStyle, QTabWidget
from PySide2.QtGui import QIcon      
from PySide2 import QtCore, QtGui                                                                                                                                                                                                                                                 

import core.setting as st
from core.camClass import camera_process as cam_avi
from core.dummy_gen import camera_process_dummy

class MainWindow(QWidget):

   def __init__(self, config, save_mode):
      super().__init__()      
      self.cams=[]
      self.config=config
      self.saving_mode=save_mode
      self.setupUI()
      
   def kill_cams(self):
      self.stop_log()
      st.kill_cams.set()


   def init_events_cams(self):
      st.init_events()

   def start_log(self):
      st.force_log.set()
      print('log start', st.force_log.is_set())

   def stop_log(self):
      st.force_log.clear()
      print('log stop', st.force_log.is_set())

   def start_saving(self):
      st.force_save.set()
      print('saving start', st.force_save.is_set())
      self.start_log()

   def start_preview(self):
      st.force_preview.set()
      print('preview start', st.force_preview.is_set())
      self.start_log()

   def stop_saving(self):
      st.force_save.clear()
      print('saving stop', st.force_save.is_set())

   def stop_preview(self):
      st.force_preview.clear()
      print('preview stop', st.force_preview.is_set())
   
   def run_cam(self, mas_sla, cam_id, pr):
      if self.saving_mode=='avi':        
         self.cams.append(cam_avi(mas_sla, cam_id, self.config, pr))
      elif self.saving_mode=='dummy':
         self.cams.append(camera_process_dummy(mas_sla, cam_id, self.config, pr))
      else:
         self.cams.append(cam_h5(mas_sla, cam_id, self.config, pr))
   
   def spawn_processes(self):
      print('spawning processes')
      for p in self.processes:
         p.start()
         print(p)

   def create_cam_processes(self):
      print('Numer of usable CPUs:',len(os.sched_getaffinity(0)))
      os.system('taskset -cp 0-%d %s' % (self.config["num_workers"]+1, os.getpid()))       
      st.init_events()
      processes=[]
      p = Process(target=self.run_cam, args=('master', 'cam1',  0 )) # framerate    
      processes.append(p)

      for pr in range(1, self.config["num_workers"]+1):
         p = Process(target=self.run_cam, args=( 'worker'+ str(pr+1), 'cam' + str(pr+1), pr)) # framerate
         processes.append(p)
      return processes

   def set_save_tab(self):
      saveTab = QWidget()
      SavingLayout = QVBoxLayout()
      save_start_button = QPushButton("Start Saving")
      save_start_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogSaveButton')))                                                                 
      save_start_button.clicked.connect(self.start_saving)     
      SavingLayout.addWidget(save_start_button)

      save_stop_button = QPushButton("Stop Saving")
      save_stop_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogDiscardButton')))                                                                 
      save_stop_button.clicked.connect(self.stop_saving)    
      SavingLayout.addWidget(save_stop_button)
      saveTab.setLayout(SavingLayout)
      return saveTab

   def set_preview_tab(self):
      previewTab = QWidget()
      PreviewingLayout = QVBoxLayout()
      preview_start_button = QPushButton("Start Preview")
      preview_start_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))                                                                
      preview_start_button.clicked.connect(self.start_preview)  
      PreviewingLayout.addWidget(preview_start_button)

      preview_start_button = QPushButton("Stop Preview")
      preview_start_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPause')))                                                                 
      preview_start_button.clicked.connect(self.stop_preview)
      PreviewingLayout.addWidget(preview_start_button)
      previewTab.setLayout(PreviewingLayout)
      return previewTab

   def build_layout(self):
      outerLayout=QVBoxLayout()
      tabs = QTabWidget()
      tabs.addTab(self.set_save_tab(), "Saving")
      tabs.addTab(self.set_preview_tab(), "Preview")
      outerLayout.addWidget(tabs)
      self.setLayout(outerLayout)

   def setupUI(self):
      self.setObjectName("Argos")
      self.setWindowModality(QtCore.Qt.NonModal)
      self.resize(487, 246)
      self.setMinimumSize(387, 156)
      self.setMaximumSize(487, 146)
      font = QtGui.QFont()
      font.setPointSize(9)
      self.setFont(font)
      self.build_layout()
      

   
   def showEvent(self, event):
      self.init_events_cams()
      self.processes=self.create_cam_processes()
      self.spawn_processes()
   
   def closeEvent(self, event):
      reply = QMessageBox.question(self, 'Quit', 'Are You Sure to Quit?', QMessageBox.No | QMessageBox.Yes)
      if reply == QMessageBox.Yes:
        self.kill_cams()
        event.accept()
      else:
         event.ignore()



def main(config, save_mode):
# Create the Qt Application                                                                         
    app = QApplication(sys.argv)                                                                          
    mw = MainWindow(config, save_mode)
    
    mw.show()
    #mw.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main(config, save_mode)