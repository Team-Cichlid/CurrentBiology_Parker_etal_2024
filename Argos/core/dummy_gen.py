import os
import time
import logging 
import threading
import multiprocessing as mp

from queue import Queue
import numpy as np
import cv2
import sys

from .saver import *
from .previewer import *
from .logging_cam import *


import core.setting as st

class camera_process_dummy():
    def __init__(self, mas_sla, cam_id, config, args, pr):
        #Camera members
        self.mas_sla = mas_sla
        self.cam_id = cam_id
        self.config=config
        self.args=args
        self.pr=pr
        self.frame=[]
        self.buffer_size=config["framerate"][pr]*2
 
        #parallel processing members
        
        self.threads=[]
        self.threads.append(threading.Thread(target=self.run_cam, args=()))
        #self.threads.append(threading.Thread(target=show_buttons, args=()))

        #self.xi=[]
    
        self.start_pipeline()
        print('Starting up xiAPI')
    
    def __del__(self): 
        for p in self.threads:
            p.join()


    def start_pipeline(self):

        try:
            st.initialize_counters()
            st.init_hotKeys()
            st.start_time=time.time()
            
            
            st.init_preview_member()
            if self.args.prv==True:
                st.force_preview=True
            else:
                st.force_preview=False
            self.threads=set_up_preview(self.config, self.config['framerate'], self.threads, self.cam_id, self.pr)
            
            st.init_saving_members()
            if self.args.save==True:
                st.force_save=True
            else:
                st.force_save=False
            self.threads=set_up_saving_q_hybrid(self.threads, self.config, self.buffer_size, self.cam_id)

            if self.cam_id==self.config['stat_cam']:
                self.threads.append (threading.Thread(target=print_stats, args=(self.config, self.cam_id)))

            
            for t in self.threads:
                t.start()
            show_buttons()
            for p in self.threads:
                p.join()

        except (KeyboardInterrupt):
            print('Shutting down all processes...')
            #sys.exit()
            for p in self.threads:
                p.join()
    
    def run_cam(self):
        print('Starting cameras')  
        try:
            self.get_frames()
            
        except KeyboardInterrupt:
            #self.send_last_frame()
            sys.exit(f'Closed {self.mas_sla} camera')

    def read_frame(self):


        return np.full((200,200),fill_value=255, dtype=np.uint8)

    def get_frames(self):
        print('Saving started')

        """if  self.args.save==True:
            for i in range(self.config["saving_queues"]):
                st.events[i].clear() """
        i=0
        while True:
            st.acquire_counter+=1
            self.frame = self.read_frame()
            
            if st.force_save==True:
                #print(st.force_save)
                st.saving_queues[i].put(self.frame) 

            if st.acquire_counter%st.fps_preview_factor==0:
                st.q_preview.put(self.frame)

            if st.acquire_counter%self.buffer_size==0 and st.force_save==True:
                i=i+1

                for k in range(self.config["saving_queues"]):
                    st.events[k].set() 

                if i>=self.config["saving_queues"]:
                    i=0
                st.events[i].clear()  
"""
    def send_last_frame(self):
        for f in range(1):
            #self.acquire()
            print(f'Generated last frame')
            st.q_saving.put(self.frame)
"""

    

  
