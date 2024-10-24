
from api import XimeaCamera
import os
import time
import threading
import multiprocessing as mp


from queue import Queue
import numpy as np
import cv2
import sys

import h5py

import subprocess   as sp

class camera_process():
    def __init__(self, mas_sla, cam_id, config, args, pr):
        #Camera members
        self.mas_sla = mas_sla
        self.framerate = config["framerate"]
        self.cam_id = cam_id
        self.exp = config["exposure"]
        self.config=config


        # stats
        self.start_time=0
        self.loss_frames=0

       # saving members 
        self.start_saving=0.0
        self.saving_counter=0
        self.frame=[]

        self.buffer_size=config["framerate"]*2
       
        #previewing members
        self.preview_counter=0

        #acquiring members
        self.acquire_counter=0
        #parallel processing members
        self.saving_queues=[]
        self.events=[] 
       
        self.q_preview=Queue()
        self.threads=[]
        self.threads.append(threading.Thread(target=self.run_cam, args=()))
        self.threads.append(threading.Thread(target=self.preview_frames, args=()))
        self.threads.append(threading.Thread(target=self.save_frames_h5, args=(0,)))
        self.threads.append(threading.Thread(target=self.save_frames_h5, args=(1,)))
        self.threads.append(threading.Thread(target=self.save_frames_h5, args=(2,)))
        
    
        self.start_pipeline()
        print('Starting up xiAPI')
    
    
    def start_pipeline(self):
        self.start_time=time.time()
        self.set_up_saving_q()
        for t in self.threads:
            t.start()
            
        if self.cam_id=='cam6':
            stats=threading.Thread(target=self.print_stats, args=())
            stats.daemon=True
            stats.start()

        for p in self.threads:
            p.join()

    def start_camera(self):
        self.xi= XimeaCamera(self.config)
        self.xi.open_camera(self.mas_sla, self.cam_id, self.exp, self.framerate)
        self.counter_selector=self.xi.get_actual_fps()
        
    def set_up_saving_q(self):
        buffer=[] 
        for i in range(self.config["saving_queues"]):
            self.saving_queues.append(buffer)
            self.events.append(threading.Event())

    def print_stats(self):
        while True:
            print('_'*80)
            print('FPS_acquiring: %f ' %(self.acquire_counter/(time.time()-self.start_time)))
            print('FPS_saving: %f ' %(self.saving_counter/(time.time()-self.start_time)))
            print('FPS_previewing: %f ' %(self.preview_counter/(time.time()-self.start_time)))
            print('Frame count:', self.acquire_counter)
            print('Cummulative Loss Frames:', self.loss_frames)
            for i in range(self.config["saving_queues"]):
                print("QUEUE SAVER_%d size: %d" %(i, len(self.saving_queues[i])))
           
           # print("QUEUE SAVER_C size:", self.q_saving_c.qsize())
            print("QUEUE PREVIEW size:", self.q_preview.qsize())
            time.sleep(1.0)

    def run_cam(self):
        print('Starting cameras')  
        try:
            self.start_camera()
            self.get_frames()
            
        except KeyboardInterrupt:
            self.send_last_frame()
            self.destroy()
            sys.exit(f'Closed {self.mas_sla} camera')

   
    def save_frames_h5(self, id):
       
        print('buffer_A1')
        
        file_path=os.path.join(self.config["saving_folder"],self.mas_sla+str(id)+'.h5')
        dataset_file=h5py.File(file_path, 'w')
        dataset_file.create_dataset('frames', (0,2048,2048), dtype=np.uint8, chunks=True, maxshape=(None,2048, 2048))
       
        dataset_file.close()
        self.events[id].wait() 
        
        
        while True:
            
            """self.saving_counter+=1*self.buffer_size
            
            """
            if self.events[id].is_set():
                with h5py.File(file_path, 'a') as hf:
                    print('+'*80)
                    hf.visit(print)
                    print('-'*80)
                    dset = hf['frames'] 
                    print(dset.shape[0])
                    dset.resize((dset.shape[0] + self.buffer_size), axis=0)
                    print('self.saving_queues[id]',len(self.saving_queues[id]))
                    dset[-self.buffer_size:] = self.saving_queues[id]
                    self.saving_counter+= self.buffer_size
                        #print('buffer_A4')
                       # out.write(self.saving_queues[id].get())
                self.saving_queues[id]=[] 

    def get_frames(self):
        print('Saving started')
        try:
            for i in range(self.config["saving_queues"]):
                self.events[i].clear() 
            i=0
            while True:
                self.acquire_counter+=1
                self.frame = self.xi.read_frame()
                self.loss_frames= self.xi.cam.get_counter_value()
                
                self.saving_queues[i].append(self.frame) 

                if self.acquire_counter%4==0:
                    k=0
                    self.q_preview.put(self.frame)

                if self.acquire_counter%self.buffer_size==0:
                    i+=1
                    for i in range(self.config["saving_queues"]):
                        self.events[i].set() 
                     
                    
                    if i>=self.config["saving_queues"]:
                        i=0
                       # self.events[i+1].set()
                       # self.events[self.config["saving_queues"]-1].set()
                    """elif i==self.config["saving_queues"]-1:
                        # self.events[i-1].set()
                         self.events[0].set()
                    else:
                      #  self.events[i-1].set()
                        self.events[i+1].set()
                    """
                    
                    self.events[i].clear()  
           
        except KeyboardInterrupt:
            out.release()
            cv2.destroyAllWindows()
            
    def preview_frames(self):    
        print('Starting Preview')  
        dim = (int(self.config["img_width"] * self.config["scale"]), int(self.config["img_heigth"] * self.config["scale"])) 
        
        while True:
            try:
                self.preview_counter+=1
                resized = cv2.resize(self.q_preview.get(), dim, interpolation = cv2.INTER_AREA)
                resized_flipped = cv2.flip(resized, -1)
                cv2.namedWindow(f'{self.mas_sla}', cv2.WINDOW_NORMAL)
                cv2.imshow(f'{self.mas_sla}', resized_flipped)
                cv2.waitKey(1)
                
            except (Empty, KeyboardInterrupt, TypeError, ValueError):
                cv2.destroyAllWindows()

    def send_last_frame(self):
        for f in range(1):
            self.acquire()
            print(f'Generated last frame')
            self.q_saving.put(self.frame)
         
    def destroy(self):
        self.xi.release()

  
