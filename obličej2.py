import cv2
import time
import numpy as np
from djitellopy import Tello

# --- Parametry pro sledování ---
FRAME_WIDTH = 960
FRAME_HEIGHT = 720
TARGET_FACE_AREA = [6000, 9000]
YAW_SENSITIVITY = 0.25
DETECTION_TIMEOUT = 5.0

def create_tracker():
    """
    Vytvoření kompatibilního CSRT trackeru podle verze OpenCV.
    """
    if int(cv2.__version__.split('.')[0]) >= 4:
        return cv2.legacy.TrackerCSRT_create() if hasattr(cv2, 'legacy') else cv2.TrackerCSRT_create()
    else:
        raise Exception("Verze OpenCV nepodporuje CSRT tracker.")

def main():
    # Připojení k dronu
    tello = Tello()
    tello.connect()

    battery_level = tello.get_battery()
    print(f"Stav baterie: {battery_level}%")
    if battery_level < 20:
        print("Kritický stav baterie, program se ukončí.")
        return

    tello.streamon()
    frame_read = tello.get_frame_read()

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    print("Vzlétám...")
    tello.takeoff()
    tello.send_rc_control(0, 0, 25, 0)
    time.sleep(2.2)
    tello.send_rc_control(0, 0, 0, 0)

    print(f"Hledám obličej po dobu {DETECTION_TIMEOUT} vteřin...")
    start_time = time.time()
    face_found = False
    tracker = None

    while time.time() - start_time < DETECTION_TIMEOUT:
        frame = frame_read.frame
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=8)

        if len(faces) > 0:
            main_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = main_face

            tracker = create_tracker()
            tracker.init(frame, (x, y, w, h))
            face_found = True
            print(" Obličej nalezen, zahajuji sledování.")
            break

        cv2.imshow("Hledani obliceje", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if not face_found:
        print(f"Obličej nenalezen do {DETECTION_TIMEOUT} vteřin. Přistávám.")
        tello.land()
        tello.streamoff()
        cv2.destroyAllWindows()
        return

    while True:
        frame = frame_read.frame
        success, bbox = tracker.update(frame)

        if success:
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            face_center_x = x + w // 2
            face_area = w * h

            error_x = face_center_x - FRAME_WIDTH // 2
            yaw_speed = int(np.clip(YAW_SENSITIVITY * error_x, -100, 100))

            fb_speed = 0
            if face_area > TARGET_FACE_AREA[1]:
                fb_speed = -25
            elif face_area < TARGET_FACE_AREA[0] and face_area > 100:
                fb_speed = 25

            tello.send_rc_control(0, fb_speed, 0, yaw_speed)

        else:
            print("Sledování selhalo, přistávám.")
            tello.land()
            break

        cv2.imshow("Sledovani", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Ukončuji program a přistávám.")
            tello.land()
            break

    tello.streamoff()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram přerušen uživatelem.")
        try:
            emergency_tello = Tello()
            emergency_tello.connect()
            emergency_tello.land()
            emergency_tello.streamoff()
        except Exception as e:
            print(f"Chyba při nouzovém přistání: {e}")
        cv2.destroyAllWindows()
