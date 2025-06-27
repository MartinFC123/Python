#funkcni, detekce obrazu
from djitellopy import Tello
import cv2
import numpy as np
import time

# Inicializace dronu
tello = Tello()
tello.connect()
print("Baterie:", tello.get_battery())

# Start kamery
tello.streamon()
frame_read = tello.get_frame_read()

# Vzlet
tello.takeoff()
time.sleep(2)

try:
    while True:
        frame = frame_read.frame
        frame = cv2.resize(frame, (480, 360))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            area = cv2.contourArea(cnt)

            if area > 1000 and len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h

                if 0.9 <= aspect_ratio <= 1.1:
                    shape = "square"
                    cv2.putText(frame, "CTVEREC", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                    print("Čtverec detekován – let doprava")
                    tello.move_right(10)
                else:
                    shape = "rectangle"
                    cv2.putText(frame, "OBDELNIK", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
                    print("Obdélník detekován – let doleva")
                    tello.move_left(10)

                # Po rozpoznání se pohne a čeká krátce
                time.sleep(2)
                break  # Zamezí vícenásobným pohybům v jednom snímku

        cv2.imshow("Obraz", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt ():
    print("Zachycen KeyboardInterrupt – přistávám.")

finally:
    tello.land()
    tello.streamoff()
    cv2.destroyAllWindows()
