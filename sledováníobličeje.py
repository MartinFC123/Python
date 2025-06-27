from djitellopy import Tello
import cv2
import time

# Inicializace Tello
tello = Tello()
tello.connect()
print(f"Baterie: {tello.get_battery()}%")

tello.streamon()
frame_read = tello.get_frame_read()

# Načtení Haar cascade pro detekci obličeje
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Vzlet
tello.takeoff()
time.sleep(2)

try:
    while True:
        frame = frame_read.frame
        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_center_x = x + w // 2
            screen_center_x = 640 // 2

            # Vizuální zobrazení
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.line(frame, (screen_center_x, 0), (screen_center_x, 480), (255, 0, 0), 2)

            offset_x = face_center_x - screen_center_x

            if abs(offset_x) > 30:  # Mrtvá zóna
                if offset_x > 0:
                    print("Obličej vpravo → otáčím vpravo")
                    tello.rotate_clockwise(10)
                else:
                    print("Obličej vlevo → otáčím vlevo")
                    tello.rotate_counter_clockwise(10)

        cv2.imshow("Tello Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    tello.land()
    cv2.destroyAllWindows()
