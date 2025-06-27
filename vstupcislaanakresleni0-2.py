from djitellopy import Tello
import time

# Inicializace
tello = Tello()
tello.connect()
print("Baterie:", tello.get_battery())

tello.takeoff()
time.sleep(2)

def dopredu(cm):
    tello.move_forward(cm)
    time.sleep(1)

def dozadu(cm):
    tello.move_back(cm)
    time.sleep(1)

def doprava(cm):
    tello.move_right(cm)
    time.sleep(1)

def doleva(cm):
    tello.move_left(cm)
    time.sleep(1)

def nahoru(cm):
    tello.move_up(cm)
    time.sleep(1)

def dolu(cm):
    tello.move_down(cm)
    time.sleep(1)

def otoc_stupne(deg):
    tello.rotate_clockwise(deg)
    time.sleep(1)

# Čísla jako letové trasy
def kresli_1():
    dopredu(50)

def kresli_0():
    dopredu(40)
    doprava(30)
    dozadu(40)
    doleva(30)
    dopredu(40)

def kresli_2():
    doprava(30)
    dopredu(20)
    doleva(30)
    dopredu(20)
    doprava(30)

# atd. — přidej další čísla podobně

# Mapa čísel
cisla = {
    '0': kresli_0,
    '1': kresli_1,
    '2': kresli_2,
    # přidej 3–9
}

# Vstup od uživatele
cislo = input("Zadej jednociferné číslo (0–9): ")

if cislo in cisla:
    print(f"Kreslím číslo {cislo} letem...")
    cisla[cislo]()
else:
    print("Neplatný vstup.")

# Ukončení
tello.land()
