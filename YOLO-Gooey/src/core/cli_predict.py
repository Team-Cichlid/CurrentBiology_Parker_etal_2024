from src.core.yolo_predict_handler import YOLOPredictHandler

class CLIPredict():

    def __init__(self, prediction_path, video_images_path, media_choice, model_folder, save_video_images, show_labels, show_conf, box_thickness):
        self.yolo_predict_handler = YOLOPredictHandler(prediction_path, video_images_path, media_choice, model_folder, save_video_images, show_labels, show_conf, box_thickness)
        return

    def launch(self):
        self.yolo_predict_handler.predict()
        return