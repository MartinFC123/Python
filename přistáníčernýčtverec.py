from djitellopy import Tello
import cv2
import numpy as np
import time

# Inicializace dronu
tello = Tello()
tello.connect()
print("Baterie:", tello.get_battery())

tello.streamon()
time.sleep(2)
tello.takeoff()
time.sleep(2)

# Hlavní smyčka
try:
    while True:
        frame = tello.get_frame_read().frame
        frame = cv2.resize(frame, (360, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detekce černé barvy
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 40])
        mask = cv2.inRange(hsv, lower_black, upper_black)

        # Najdi obrys čtverce
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Najdi největší černý čtverec
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)

            if area > 1500:
                # Najdi střed čtverce
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # Nakresli střed
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                    # Najdi odchylku od středu obrazu
                    error_x = cx - 180
                    error_y = cy - 120

                    # Priblizovani a vyrovnání pozice
                    if abs(error_x) > 20:
                        tello.send_rc_control(int(error_x / -10), 0, 0, 0)
                    elif abs(error_y) > 20:
                        tello.send_rc_control(0, int(error_y / -10), 0, 0)
                    else:
                        # Pokud je střed zarovnaný, sestupuj
                        print("Zarovnáno. Sestupujeme...")
                        tello.send_rc_control(0, 0, -20, 0)
                        time.sleep(1)
                        tello.send_rc_control(0, 0, 0, 0)
                        time.sleep(0.5)

                        # Kontrola, jestli jsme dostatečně nízko
                        height = tello.get_height()
                        print("Výška:", height)
                        if height < 50:
                            print("Přistávám...")
                            tello.land()
                            break
                else:
                    print("Nelze vypočítat střed.")
        else:
            print("Černý čtverec nenalezen.")
            tello.send_rc_control(0, 0, 0, 0)

        # Zobrazení
        cv2.imshow("Obraz", frame)
        cv2.imshow("Maska", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.streamoff()
    cv2.destroyAllWindows()
    tello.land()
