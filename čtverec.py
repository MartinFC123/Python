from djitellopy import Tello
tello = Tello ()
tello.connect ()
tello.takeoff ()
tello.get_height ()

for _ in range (4):
    tello.rotate_clockwise (90)
    tello.land ()
