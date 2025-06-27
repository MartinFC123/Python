from djitellopy import Tello
import cv2
import time
import numpy as np
#nutné pip install djitellopy opencv-python numpy

# Inicializace dronu
tello = Tello()
tello.connect()
print("Baterie:", tello.get_battery(), "%")

# Spuštění videostreamu
tello.streamon()
time.sleep(2)

# Vzlet
tello.takeoff()
time.sleep(2)

found_black = False

while not found_black:
    frame = tello.get_frame_read().frame
    frame = cv2.resize(frame, (360, 240))

    # Převod na HSV pro detekci černé barvy
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Rozsah pro černou barvu v HSV
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])

    # Maska pro černou
    mask = cv2.inRange(hsv, lower_black, upper_black)

    # Výpočet plochy černé barvy
    black_area = cv2.countNonZero(mask)
    cv2.imshow("Maska", mask)
    cv2.imshow("Kamera", frame)

    if black_area > 1000:  # Práh detekce černé
        print("Černá barva nalezena!")
        found_black = True
        tello.send_rc_control(0, 0, 0, 0)
        time.sleep(5)
        tello.move_down(50)
        break
    else:
        tello.send_rc_control(0, 0, 25, 0)  # Stoupej nahoru
        time.sleep(0.3)
        tello.send_rc_control(0, 0, 0, 0)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Ukončení
tello.land()
tello.streamoff()
cv2.destroyAllWindows()
