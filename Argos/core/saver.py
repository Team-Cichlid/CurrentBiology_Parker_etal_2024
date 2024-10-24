
import cv2
import os
import threading
import time
import numpy as np

from datetime import date, datetime
from queue import Queue


import core.setting as st


def save_frames_buff_avi(id, config, cam_id, buffer_size, pr):
        try:
            print('buffer_'+str(id))

            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            saving_folder=os.path.join(config["saving_folder"], cam_id, st.today)
            if os.path.exists(saving_folder) is False:
                os.makedirs(saving_folder)
            file_path=os.path.join(saving_folder, st.datetime + '0'+ cam_id.replace('cam','')+ str(id)+'.avi')
            st.force_save.wait()
            print('Saving Started')
            out= cv2.VideoWriter(file_path, fourcc, config["framerate"][pr], (config["img_heigth"], config["img_width"]), False) # False for no colour
            
            while True:
                for i in range(buffer_size):
                    st.saving_counter+=1
                    out.write(cv2.flip(st.saving_queues[id].get(), -1))

                if st.force_save.is_set() is False:
                    print('Closing saving')
                    out.release()
                    break

        except KeyboardInterrupt:
            print('Closing saving')
            out.release()         


def save_frames_buff_avi_int(id, config, cam_id, buffer_size, pr):
        try:
            print('buffer_'+str(id))
            
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            saving_folder=os.path.join(config["saving_folder"], cam_id, st.today)
            if os.path.exists(saving_folder) is False:
                os.makedirs(saving_folder)
            datetime_video=datetime.now().strftime("%Y%m%d%H%M%S")
            file_path=os.path.join(saving_folder, datetime_video + '0'+ cam_id.replace('cam','')+ str(id)+'.avi')
            print('Saving Video interval')
            out= cv2.VideoWriter(file_path, fourcc, config["framerate"][pr], (config["img_heigth"], config["img_width"]), False) # False for no colour
            time_video=time.time()
            while True:
                for i in range(buffer_size):
                    st.saving_counter+=1
                    out.write(cv2.flip(st.saving_queues[id].get(), -1))

                if (time.time()-time_video)>=config["video_length"]*60:
                    print('Closing video every...')
                    out.release()
                    break

        except KeyboardInterrupt:
            print('Closing saving')
            out.release()         
        
def save_frames_images(id, config, cam_id, buffer_size):
        try:
            st.preview_counter+=1
            saving_folder=os.path.join(config["saving_folder"], cam_id, st.today)
            if os.path.exists(saving_folder) is False:
                os.makedirs(saving_folder)
            datetime_image=datetime.now().strftime("%Y%m%d%H%M%S")
            file_path=os.path.join(saving_folder, datetime_image + '0'+ cam_id.replace('cam','')+ str(id)+'.JPEG')
            print('Saving image:',file_path)
            flipped = cv2.flip(st.saving_queues[id].get(), -1)
            #flipped=np.full((200,200),fill_value=255, dtype=np.uint8)
            cv2.imwrite(file_path,flipped)

        except KeyboardInterrupt:
            print('problem saving image:',file_path)
        


def time_manager(id, config, cam_id, buffer_size, pr):
    st.force_save.wait()
    print('Starting Time Manager')
    #timer_event=threading.Event()

    time_interval_vdo=time.time()
    time_interval_img=time.time()
    save_frames_images(id, config, cam_id, buffer_size)
    while True:

        time_image=abs(time_interval_img-time.time())
        time_video=abs(time_interval_vdo-time.time())

        if time_image>=config["image_every"]*60 and time_video<=config["video_every"]*60 :
            save_frames_images(id, config, cam_id, buffer_size)
            time_interval_img=time.time()
            
        elif time_image>=config["image_every"]*60 and time_video>=config["video_every"]*60:
            save_frames_buff_avi_int(id, config, cam_id, buffer_size, pr)
            time_interval_vdo=time.time()
            time_interval_img=time.time()
            
        else:
            if st.saving_queues[id].qsize()!=0:
                dump_frame=st.saving_queues[id].get()
        if st.force_save.is_set() is False:
            print('Closing saving')
            break


def set_up_saving_q_hybrid(threads, config, buffer_size, cam_id, pr):
    
    for i in range(config["saving_queues"]):
        threads.append(threading.Thread(target=time_manager, args=(i, config, cam_id, buffer_size, pr, )))
        st.saving_queues.append(Queue(maxsize=buffer_size))
        st.events.append(threading.Event())

    return threads

def set_up_saving_q_cont(threads, config, buffer_size, cam_id, pr, ):
    
    for i in range(config["saving_queues"]):
        threads.append(threading.Thread(target=save_frames_buff_avi, args=(i, config, cam_id, buffer_size, pr, )))
        st.saving_queues.append(Queue(maxsize=buffer_size))
        st.events.append(threading.Event())

    return threads

