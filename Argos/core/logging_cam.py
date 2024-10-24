import time
import threading
import logging
import os
from datetime import date, datetime

import core.setting as st


def print_stats(config):
    st.force_log.wait()
    logging.info('log Started')
    saving_folder=os.path.join(config["saving_folder"], 'cam1', st.today)
    if os.path.exists(saving_folder) is False:
        os.makedirs(saving_folder)
    datetime_video=datetime.now().strftime("%Y%m%d%H%M%S")
    file_path=os.path.join(saving_folder, datetime_video + '0'+ 'cam1.log')
    logging.FileHandler(filename=file_path, mode='w')
    logging.basicConfig(filename=file_path, filemode='w')
    
    try:
        while True:
            if st.force_log.is_set():
                print('_'*80)
                logging.info('FPS_acquiring: %f ' %(st.acquire_counter/(time.time()-st.start_time)))
                logging.info('FPS_acquiring: %f ' %(st.acquire_counter/(time.time()-st.start_time)))
                logging.info('FPS_saving: %f ' %(st.saving_counter/(time.time()-st.start_time)))
                logging.info('FPS_previewing: %f ' %(st.preview_counter/(time.time()-st.start_time)))
                logging.info('Frame count: %d' %(st.acquire_counter))
                logging.info('Cummulative Loss Frames: %d' %(st.loss_frames))
                if  st.force_save.is_set():
                    for i in range(config["saving_queues"]):
                        logging.info("QUEUE SAVER_%d size: %d" %(i, st.saving_queues[i].qsize()))
                
                # logging.info("QUEUE SAVER_C size:", self.q_saving_c.qsize())
                logging.info("QUEUE PREVIEW size: %d" %( st.q_preview.qsize()))
                time.sleep(3.0)
                if st.force_log.is_set() is False:

                    break

    except (KeyboardInterrupt, TypeError, ValueError):
            print('Closing log')
           
    return 

def start_daemon_stats(config):
    stats=threading.Thread(target=print_stats, args=(config, ))
    #stats.daemon=True
    return stats