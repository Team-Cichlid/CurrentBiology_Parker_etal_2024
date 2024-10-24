from .ximea import xiapi
import numpy
from time import sleep

class XimeaCamera():
    """Class for simple control of a Ximea camera.
    Uses ximea API. Module documentation `here
    <https://www.ximea.com/support/wiki/apis/Python>`_.
    """
    def __init__(self, config):
        self.buffer_policy = config["buffer_policy"]
        self.buffer_queue_size = config["buffer_queue_size"]
        self.acq_buffer_size = config["buffer_size"] #tweaking 
        #self.im = xiapi.Image()

        try: # Test if API for the camera is available
            self.cam = xiapi.Camera()
        except NameError:
            raise Exception(
                "The xiapi package must be installed to use a Ximea camera!")
        # print('Connected cameras: ' + str(self.cam.get_number_devices()))

    def open_camera(self, mas_sla, cam_id, exp, fr):
        self.cam.open_device_by('XI_OPEN_BY_USER_ID', cam_id)
        # print('Acq_timing_mode: ' + str(self.cam.get_acq_timing_mode()))

        # Buffer settings
        self.cam.set_buffer_policy(self.buffer_policy)
        self.cam.set_buffers_queue_size(self.buffer_queue_size)
        self.cam.set_acq_buffer_size(self.acq_buffer_size)

        # Acquisition settings
        self.cam.set_exposure(exp)
        #self.cam.set_imgdataformat('XI_MONO8')

        # make master or worker
        if mas_sla == 'master':
            self.cam.set_gpo_selector('XI_GPO_PORT1')
            self.cam.set_gpo_mode('XI_GPO_FRAME_ACTIVE')
            self.cam.set_acq_timing_mode("XI_ACQ_TIMING_MODE_FRAME_RATE_LIMIT")
            self.cam.set_framerate(fr)

        elif mas_sla == 'worker':
            self.cam.set_gpi_selector('XI_GPI_PORT1')
            self.cam.set_gpi_mode('XI_GPI_TRIGGER')
            self.cam.set_trigger_source('XI_TRG_EDGE_RISING')
            

        self.im = xiapi.Image()
        self.cam.start_acquisition()

    def read_frame(self):
        try:
            self.cam.get_image(self.im)
            frame = self.im.get_image_data_numpy()

        except xiapi.Xi_error:
            frame = None

        return frame

    
    def get_actual_fps(self):
       # counter=self.cam.set_counter_selector('XI_CNT_SEL_TRANSPORT_SKIPPED_FRAMES')#loss frames in communication 
        counter=self.cam.set_param('counter_selector', 'XI_CNT_SEL_API_SKIPPED_FRAMES')#lossed frames in API 
       #counter=self.cam.set_counter_selector('XI_CNT_SEL_TRANSPORT_TRANSFERRED_FRAMES')#actual  
    


    def release(self):
        self.cam.stop_acquisition()
        self.cam.close_device()
