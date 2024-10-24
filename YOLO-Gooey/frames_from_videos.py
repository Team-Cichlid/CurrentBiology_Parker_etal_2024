from datetime import datetime
from tqdm import tqdm
from glob import glob
import os
import cv2
import argparse
from datetime import timedelta, datetime

MINUTES = [7,14,20]

VIDEO_EXTS = ['.avi']
SAVE_EXT = '.JPEG'

def get_frame_name(path, seconds):
    '''The following file name format is assumed:

       20220314_150533_020.avi
    '''
    # Remove video extension
    video_name=os.path.splitext(path)[0]

    # Separate cam id from video_name
    *video_name_str, camId = video_name.split('_', 2)
    video_name_str = ''.join(video_name_str)
    video_datetime=datetime.strptime(video_name_str, "%Y%m%d%H%M%S") + timedelta(seconds=seconds)
    frame_name=video_datetime.strftime("%Y%m%d_%H%M%S") + "_" + camId + SAVE_EXT
    return frame_name

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract frames from video in <data> folder and save them as images.')
    parser.add_argument('--data', '-d', help='path to data folder containing videos.', required=True)
    data = parser.parse_args().data

    if not os.path.exists(data):
        print('Folder path not found :(')
        exit(-1)
    if os.path.isfile(data):
        print('Only folders are supported and not single video paths :( .Please pass a folder (current folder is represented by a dot . ).')
        exit(-1)
    video_paths = [p for p in os.listdir(data) if os.path.splitext(p)[-1] in VIDEO_EXTS]
    for path in tqdm(video_paths, colour='green', desc='videos processed'):
        reader = cv2.VideoCapture(os.path.join(data,path))
        fps = reader.get(cv2.CAP_PROP_FPS)
        for minute in MINUTES:
            reader.set(cv2.CAP_PROP_POS_FRAMES, minute*60*fps-1)
            success, image = reader.read()
            if not success:
                break
            frame_name=get_frame_name(path, minute*60)
            cv2.imwrite(os.path.join(data, frame_name), image)
