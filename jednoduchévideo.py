from djitellopy import Tello
import cv2
import time
import numpy

tello = Tello ()
tello.connect ()
tello.takeoff ()
tello.move_up(20)
tello.streamon ()
frame_read = tello.get_frame_read()
fourcc = cv2.VideoWriter_fourcc (*'XVID')
video_writer = cv2.VideoWriter ("video2.avi", cv2.VideoWriter_fourcc(*'XVID'), 30, (960, 720))
start_time = time.time ()
while time.time () - start_time < 2:
    frame = frame_read.frame
    #zapiš jeden snímek do výstupního video souboru
    video_writer.write (frame)
    cv2.imshow("Tello Video", frame)
    
video_writer.release ()
tello.streamoff ()
tello.move_down(20)
tello.land ()
