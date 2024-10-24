import threading
import cv2
import time

import core.setting as st


def preview_frames(config, cam_id ):    
        dim = (int(config["img_width"] * config["scale"]), int(config["img_heigth"] * config["scale"])) 
        st.force_preview.wait()
        print('Preview Started') 
        try:
            while True:
                    st.preview_counter+=1
                    #print("Q----------:", st.q_preview.qsize())
                    #cv2.imwrite('argos_out/'+str(st.preview_counter)+'.jpg',st.q_preview.get())
                    resized = cv2.resize(st.q_preview.get(), dim, interpolation = cv2.INTER_AREA)
                    resized_flipped = cv2.flip(resized, -1)
                    print('1'*80)
                    cv2.namedWindow(f'{cam_id}', cv2.WINDOW_NORMAL)
                    print('2'*80)
                    #cv2.line(resized_flipped, (0, 120), (1630, 120), color=(0, 211, 255), thickness=20)
                    cv2.imshow(f'{cam_id}', resized_flipped)
                    print('3'*80)
                    cv2.waitKey(1)

                    if st.force_preview.is_set() is False:
                        print('Closing preview')
                        cv2.destroyAllWindows()
                        st.force_preview.wait() 

        except (KeyboardInterrupt, TypeError, ValueError):
            print('Closing preview')
            cv2.destroyAllWindows()

def set_up_preview(config, framerate, threads, cam_id, pr):

    if framerate[pr]>90:
        st.fps_preview_factor=5
    elif (framerate[pr]>70 and framerate[pr]<=90 ):
        st.fps_preview_factor=4
    elif (framerate[pr]>40 and framerate[pr]<=70 ):
        st.fps_preview_factor=3
    elif (framerate[pr]<=40 ):
        st.fps_preview_factor=2

    threads.append(threading.Thread(target=preview_frames, args=(config, cam_id)))
    return threads