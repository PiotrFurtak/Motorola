from Sprite import Sprite
from math import cos,sin,radians
import pygame
class FrontWheels(Sprite):
    def __init__(self,window,coords,image,centre_point):
        self.pressed_keys = set()
        Sprite.__init__(self,window,coords,image,centre_point,0)


class Car(Sprite):
    def __init__(self,window,coords,image,centre_point,is_player=False):
        Sprite.__init__(self,window,coords,image,centre_point,0,is_player=is_player)
        self.oFrontWheels = FrontWheels(window,coords,image,(1,19))
        Sprite.forward(self,-48)
        self.stear = 0
        self.joystick_x = 0
        self.joystick_y = 0
        self.velocity = 0
        self.last_pos = (0,0,0,0,0,0)
        self.is_braking = False  # Czy samochód hamuje
        self.drift_offset = 0  # Kąt poślizgu (różnica między kątem jazdy a kątem samochodu)

    def forward(self,distance):
        self.oFrontWheels.forward(distance)
        Sprite.forward(self,-60)
        self.point_at(self.oFrontWheels.coords)
        Sprite.forward(self,60)
        self.set_position(self.oFrontWheels.coords)

    def get_pressed_keys(self, pressed_keys):
        self.joystick_y = 0
        self.joystick_x = 0
        self.is_braking = False  # Resetuj stan hamowania

        self.pressed_keys = pressed_keys

        # Ruch do przodu i do tyłu
        if self.pressed_keys.intersection({pygame.K_UP, pygame.K_w}):
            self.joystick_y += 1
        if self.pressed_keys.intersection({pygame.K_DOWN, pygame.K_s}):
            self.joystick_y -= 1

        # Skręt
        if self.pressed_keys.intersection({pygame.K_LEFT, pygame.K_a}):
            self.joystick_x += 1
        if self.pressed_keys.intersection({pygame.K_RIGHT, pygame.K_d}):
            self.joystick_x -= 1

        # Hamowanie
        if pygame.K_SPACE in self.pressed_keys:
            self.is_braking = True

    def turn(self):
        if self.joystick_x == 0:
            self.stear *= 0.3
        self.stear += 4 * self.joystick_x
        self.stear *= 0.9
        self.oFrontWheels.set_angle(self.angle + self.stear)

    def move(self):
        self.last_pos = (self.x, self.y, self.angle, self.oFrontWheels.x, self.oFrontWheels.y, self.oFrontWheels.angle)

        # Jeśli hamujemy
        if self.is_braking:
            self.velocity *= 0.9  # Redukcja prędkości podczas hamowania
            if abs(self.velocity) < 0.5:
                self.velocity = 0  # Zatrzymaj samochód, jeśli prędkość jest bardzo mała

            # Drift podczas hamowania i skręcania
            if self.joystick_x != 0:
                drift_intensity = self.joystick_x * self.velocity * 0.1  # Intensywność poślizgu
                self.drift_offset += drift_intensity
                self.drift_offset = max(-30, min(30, self.drift_offset))  # Ogranicz drift do ±30 stopni
            else:
                # Stopniowe wygaszanie driftu, jeśli nie skręcamy
                self.drift_offset *= 0.9

        self.velocity += 2 * self.joystick_y  # Przyspieszanie
        self.velocity *= 0.86  # Tarcie podczas jazdy
        self.drift_offset *= 0.9  # Zmniejsz drift, gdy nie hamujemy

        # Uwzględnienie driftu w ruchu
        drifted_angle = self.angle + self.drift_offset
        if self.is_braking:
            x = self.velocity * cos(radians(drifted_angle))
            y = self.velocity * sin(radians(drifted_angle))
            self.oFrontWheels.change_position(x,-y)

        # Skręt i aktualizacja przednich kół
        self.forward(self.velocity)
        self.turn()

    def back(self):
        self.set_position(self.last_pos[0:2])
        self.set_angle(self.last_pos[2])
        self.oFrontWheels.set_position(self.last_pos[3:5])
        self.oFrontWheels.set_angle(self.last_pos[5])