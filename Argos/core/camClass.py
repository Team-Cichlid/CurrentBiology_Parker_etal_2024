
from .api import XimeaCamera
import os
import time
import logging 
import threading
import multiprocessing as mp

from queue import Queue
import numpy as np
import cv2
import sys

import subprocess   as sp

from .saver import *
from .previewer import *
from .logging_cam import *

import core.setting as st

class camera_process():
    def __init__(self, mas_sla, cam_id, config, pr):
        #Camera members
        self.mas_sla = mas_sla
        self.cam_id = cam_id
        self.config=config
        self.pr=pr
        self.frame=[]
        self.buffer_size=config["framerate"][pr]*2
        self.hybrid=config["hybrid_cams"][pr] #1 means yes it is hybrid
 
        #parallel processing members
        
        self.threads=[]
        self.threads.append(threading.Thread(target=self.run_cam, args=()))
        #self.threads.append(threading.Thread(target=show_buttons, args=()))

        #self.xi=[]
        print('------------------->Starting', self.mas_sla)
        self.start_pipeline()
        
    
    def __del__(self):
        print('------------------->destroying', self.mas_sla)
        self.destroy()
        st.force_save.clear()
        time.sleep(4)
        for p in self.threads:
            p.join()


    def start_pipeline(self):

        try:
            st.initialize_counters()
            st.start_time=time.time()
            
            st.init_preview_member()
            self.threads=set_up_preview(self.config, self.config['framerate'], self.threads, self.cam_id, self.pr)
            
            st.init_saving_members()
            if self.hybrid==1:
                print('camera %s is hybird'%(self.mas_sla))
                self.threads=set_up_saving_q_hybrid(self.threads, self.config, self.buffer_size, self.cam_id, self.pr)
            else:
                print('camera %s is continuous'%(self.mas_sla))
                self.threads=set_up_saving_q_cont(self.threads, self.config, self.buffer_size, self.cam_id, self.pr)

            for t in self.threads:
                t.start()

            if self.cam_id==self.config['stat_cam']:
                stats=start_daemon_stats(self.config)
                stats.start()

            st.kill_cams.wait()
            self.__del__()

        except (KeyboardInterrupt, TypeError, ValueError):
            print('Shutting down all processes...')
            self.destroy()
            for p in self.threads:
                p.join()

    def start_camera(self):
        
        self.xi= XimeaCamera(self.config)
        self.xi.open_camera(self.mas_sla, self.cam_id, self.config['exposure'][self.pr], self.config["framerate"][self.pr])
        self.counter_selector=self.xi.get_actual_fps()
        
    
    def run_cam(self):
        print('Starting cameras')  
        try:
            self.start_camera()
            self.get_frames()
            
        except KeyboardInterrupt:
            #self.send_last_frame()
            self.destroy()
            sys.exit(f'Closed {self.mas_sla} camera')


    def get_frames(self):
        print('Saving started')

        """if  self.args.save==True:
            for i in range(self.config["saving_queues"]):
                st.events[i].clear() """
        i=0
        while True:
            st.acquire_counter+=1
            self.frame = self.xi.read_frame()
            st.loss_frames= self.xi.cam.get_counter_value()
            
            if st.force_save.is_set():
                #print(st.force_save)
                st.saving_queues[i].put(self.frame) 

            if st.acquire_counter%st.fps_preview_factor==0 and st.force_preview.is_set():
                st.q_preview.put(self.frame)

    
    def destroy(self):
        self.xi.release()
        print('ximea cam %s detroyed'%(self.mas_sla))
    
"""
    def send_last_frame(self):
        for f in range(1):
            #self.acquire()
            print(f'Generated last frame')
            st.q_saving.put(self.frame)
"""

    

  
