from queue import Queue
from datetime import date, datetime
import multiprocessing

def initialize_counters():
    global saving_counter
    saving_counter=0

    global preview_counter
    preview_counter=0

    global acquire_counter
    acquire_counter=0

    global loss_frames
    loss_frames=0

    global start_time
    start_time=0

    global today
    today=date.today().strftime("%Y%m%d")

    global datetime
    datetime=datetime.now().strftime("%Y%m%d%H%M%S")

def init_saving_members():
    global saving_queues
    saving_queues=[]

    global events
    events=[] 

def init_preview_member():
    global q_preview
    q_preview=Queue()

    global fps_preview_factor
    fps_preview_factor=1

def init_events():
    global force_save
    force_save=multiprocessing.Event()
    force_save.clear()

    global force_preview
    force_preview=multiprocessing.Event()
    force_preview.clear()

    global force_log
    force_log=multiprocessing.Event()
    force_log.clear()

    global kill_cams
    kill_cams=multiprocessing.Event()
    kill_cams.clear()


"""
def init_synch_vars():
    global semaphore_save_stats
    semaphore_save_stats=threading.Semaphore()
"""