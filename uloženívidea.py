import cv2
import numpy as np
import time
from time import sleep
from djitellopy import Tello  # Ujisti se, že máš nainstalovaný balíček djitellopy

# Inicializace dronu
tello = Tello()
tello.connect()
print("Baterie:", tello.get_battery())

# Spuštění videostreamu
tello.streamon()
frame_read = tello.get_frame_read()

# Nastavení VideoWriteru
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_writer = cv2.VideoWriter('vystup.avi', fourcc, 30.0, (960, 720))  # 960x720 je výchozí rozlišení videa Tellu

tello.takeoff()
print("Výška:", tello.get_height())

#tello.rotate_command_by_yaw

for _ in range(4):
    tello.move_forward(30)
    time.sleep(1)
    tello.move_back(30)

#tello.send_rc_control(0, 0, 50, 0)
#sleep(2)

tello.send_rc_control(0, 0, 0, -50)
sleep(1)

# Nahrávej video 10 sekund (např.)
start_time = time.time()
while time.time() - start_time < 10:
    frame = frame_read.frame
    video_writer.write(frame)
    cv2.imshow("Tello Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tello.land()

# Uvolnění prostředků
video_writer.release()
cv2.destroyAllWindows()
tello.streamoff()
