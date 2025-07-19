from djitellopy import Tello
import time
import random

# Inicializace dronu
tello = Tello()

# Připojení k dronu
tello.connect()
print(f"Battery: {tello.get_battery()}%")

# Vzlet
tello.takeoff()
time.sleep(2)

# Freestyle pohyby
try:
    for i in range(10):  # 10 náhodných pohybů
        move = random.choice(['forward', 'back', 'left', 'right', 'up', 'down', 'flip'])
        distance = random.randint(20, 50)  # vzdálenost v cm

        print(f"Move: {move}, Distance: {distance}")

        if move == 'forward':
            tello.move_forward(distance)
        elif move == 'back':
            tello.move_back(distance)
        elif move == 'left':
            tello.move_left(distance)
        elif move == 'right':
            tello.move_right(distance)
        elif move == 'up':
            tello.move_up(distance)
        elif move == 'down':
            tello.move_down(distance)
        elif move == 'flip':
            flip_dir = random.choice(['l', 'r', 'f', 'b'])  # left, right, front, back
            tello.flip(flip_dir)

        time.sleep(1)  # pauza mezi pohyby

except KeyboardInterrupt:
    print("Přerušeno uživatelem")

# Přistání
tello.land()
tello.end()
