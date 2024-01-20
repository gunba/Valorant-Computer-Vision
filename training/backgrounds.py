import cv2
import os

def process_video(video):
    capture = cv2.VideoCapture(video)
    ticks = 0

    while True:
        grab = capture.grab()
        if grab:
            msec = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if msec >= ticks:
                # Capture every Xth frame based on tickrate.
                _, frame = capture.retrieve()

                map = frame[95:(95+855), 471:(471+1127)]
                map = cv2.cvtColor(map, cv2.COLOR_RGB2RGBA)

                vname = video.split('/')[-1]

                # Store it
                cv_error(map, name=str(ticks)+'-'+vname, folder='backgrounds')

                print(msec)

                ticks += 1
        else:
            # Finish
            break

def cv_error(image, name, folder="/data"):
    print(folder + '/' + str(name) + ".png")
    cv2.imwrite(folder + '/' + str(name) + ".png", image)
    return None

process_video("videos/1.mp4")
process_video("videos/2.mp4")
process_video("videos/3.mp4")
process_video("videos/4.mp4")
process_video("videos/5.mp4")
process_video("videos/6.mp4")
process_video("videos/7.mp4")
process_video("videos/8.mp4")
process_video("videos/9.mp4")
process_video("videos/10.mp4")
process_video("videos/11.mp4")
process_video("videos/12.mp4")
process_video("videos/13.mp4")
process_video("videos/14.mp4")
process_video("videos/15.mp4")
process_video("videos/16.mp4")
process_video("videos/17.mp4")

