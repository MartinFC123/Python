from djitellopy import Tello
import cv2
import numpy as np
import time

# Připojení k dronu
tello = Tello()
tello.connect()
print("Baterie:", tello.get_battery())

tello.streamon()
frame_read = tello.get_frame_read()

tello.takeoff()
time.sleep(2)

try:
    while True:
        frame = frame_read.frame
        frame = cv2.resize(frame, (480, 360))

        # Převedení na HSV pro detekci bílé
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 55, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Najdi kontury
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Najdi největší čáru
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)

            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])  # střed čáry
                cy = int(M["m01"] / M["m00"])

                # Výpočet posunu oproti středu obrazu
                error = cx - 240  # 480/2 = 240

                if abs(error) < 20:
                    tello.send_rc_control(0, 20, 0, 0)  # dopředu
                elif error > 0:
                    tello.send_rc_control(10, 10, 0, 0)  # vpravo + dopředu
                else:
                    tello.send_rc_control(-10, 10, 0, 0)  # vlevo + dopředu
            else:
                tello.send_rc_control(0, 0, 0, 0)

        else:
            tello.send_rc_control(0, 0, 0, 0)  # stop, pokud čára není vidět

        # Zobrazení obrazu (volitelné)
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.send_rc_control(0, 0, 0, 0)
    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()

