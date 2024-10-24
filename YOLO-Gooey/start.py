
try:
    import os
    import sys
    import argparse
    from src.core.cli_predict import CLIPredict
    from src.core.home import Home
except Exception as e:
    print('-'*20)
    print('Encountered following error:')
    print(e)
    print('-'*10)
    print(f'Please activate/install \'yolo_gooey\' environment.')
    print('-'*20)
    sys.exit(-1)

def main(args):
    check_base_folder()
    if args.cli:
        cli_predict = CLIPredict(args.save_path, args.data, '', args.model, args.save_pred, args.show_labels, args.show_conf, args.box_thickness)
        cli_predict.launch()
    else:
        home = Home()
        home.launch()

def check_base_folder():
    if os.path.basename(os.getcwd()) != 'YOLO-Gooey':
        print('-'*20)
        print('Please launch the program from within the \'/YOLO-Gooey\' directory.')
        print('-'*20)
        sys.exit(-1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run training/prediction using YOLOv5 with GUI/CLI interface')
    parser.add_argument('-cli', action='store_true', help='use command line interface (CLI) instead of graphical user interface (GUI)', required=False)
    parser.add_argument('-data', required='-cli' in sys.argv, help='path to data')
    parser.add_argument('-model', required='-cli' in sys.argv, help='path to model folder')
    parser.add_argument('-save_path', nargs='?', const='', type=str, default='', help='save output path')
    parser.add_argument('-save_pred', action='store_true', required=False, help='whether to save bboxes overlayed on images/videos or not')
    parser.add_argument('-show_labels', action='store_true', required=False, help='whether to show labels on bboxes')
    parser.add_argument('-show_conf', action='store_true', required=False, help='whether to show confidence values on bboxes')
    parser.add_argument('-box_thickness', nargs='?', const=1, type=int, default=3, help='bbox thickness')

    args = parser.parse_args()
    main(args)
