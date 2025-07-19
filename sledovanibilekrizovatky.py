from djitellopy import Tello
import cv2
import numpy as np
import time
 
 # Inicializace
tello = Tello()
tello.connect()
print("Baterie:", tello.get_battery())
tello.streamon()
 
... # PID konstanty
Kp = 0.4
Ki = 0.0
Kd = 0.2
prev_error = 0
integral = 0
... 
... # Video výstup
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('tello_line_follow.avi', fourcc, 20.0, (480, 360))
... 
... # Vzlet
frame_read = tello.get_frame_read()
tello.takeoff()
time.sleep(2)
... 
try:
     while True:
        frame = frame_read.frame
        frame = cv2.resize(frame, (480, 360))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
 
         # BÍLÁ čára
        white_mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 40, 255]))
 
        # DALŠÍ značky – červená a modrá
        red_mask = cv2.inRange(hsv, np.array([0, 120, 120]), np.array([10, 255, 255]))
        blue_mask = cv2.inRange(hsv, np.array([100, 150, 0]), np.array([140, 255, 255]))

        # Najdi největší bílou čáru
        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)

            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                error = cx - 240

                # PID řízení
                integral += error
                derivative = error - prev_error
                yaw_speed = int(Kp * error + Ki * integral + Kd * derivative)
                yaw_speed = max(min(yaw_speed, 30), -30)  # omezení

                tello.send_rc_control(yaw_speed, 20, 0, 0)  # otáčej + let dopředu
                prev_error = error
        else:
            tello.send_rc_control(0, 0, 0, 0)

        # REAKCE na značky
        if cv2.countNonZero(red_mask) > 500:
            print("🔴 Detekována červená – otáčím vlevo")
            tello.send_rc_control(-30, 0, 0, 0)
            time.sleep(1)

        if cv2.countNonZero(blue_mask) > 500:
            print("🔵 Detekována modrá – zastavuji")
            tello.send_rc_control(0, 0, 0, 0)
            time.sleep(3)

        # Uložení videa
        out.write(frame)

        # Zobrazení (volitelné)
        cv2.imshow("Frame", frame)
        cv2.imshow("White Mask", white_mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.send_rc_control(0, 0, 0, 0)
    tello.land()
    tello.streamoff()
    out.release()
