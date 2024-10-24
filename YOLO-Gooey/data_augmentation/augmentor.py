from augmentor_utils import *

# Data augmentation script.
# Useful for generating additional annotations for both object detection (PascalVOC format) and object classification annotations.
if __name__ == '__main__':
    path = get_data_path()
    backup_warning()
    data_type = get_data_type(path)
    start = time()
    if data_type == 'classifier':
        augment_classifier_data(path)
    elif data_type == 'detector':
        augment_detector_data(path)
    print('Finished. Time taken {:.2f} seconds.'.format(time()-start))
