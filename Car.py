from Sprite import Sprite
from math import cos,sin,radians
import pygame

class Car(Sprite):
    def __init__(self,window,coords,image,centre_point,is_player=False):
        Sprite.__init__(self,window,coords,image,centre_point,0,is_player=is_player)
        self.stear = 0
        self.joystick_x = 0
        self.joystick_y = 0
        self.last_pos = (0,0,0)
        self.is_braking = False  # Czy samochód hamuje
        self.pressed_keys = set()
        self.acceleration = 0
        self.Xacceleration = 0
        self.Yacceleration = 0
        self.velocity = 0
        self.Xvelocity = 0
        self.Yvelocity = 0
        self.drift = 0
        self.tile_id = 0
        self.loops = 0

    def get_pressed_keys(self, pressed_keys):
        self.joystick_y = 0
        self.joystick_x = 0
        self.is_braking = False  # Resetuj stan hamowania

        self.pressed_keys = pressed_keys

        # Ruch do przodu i do tyłu
        if pygame.K_UP in self.pressed_keys or pygame.K_w in self.pressed_keys:
            self.joystick_y += 1
        if pygame.K_DOWN in self.pressed_keys or pygame.K_s in self.pressed_keys:
            self.joystick_y -= 1

        # Skręt
        if pygame.K_LEFT in self.pressed_keys or pygame.K_a in self.pressed_keys:
            self.joystick_x += 1
        if pygame.K_RIGHT in self.pressed_keys or pygame.K_d in self.pressed_keys:
            self.joystick_x -= 1

        # Hamowanie
        if pygame.K_SPACE in self.pressed_keys:
            self.is_braking = True

    def turn(self):
        if self.joystick_x == 0:
            self.stear *= 0.3
        self.stear += 4 * self.joystick_x
        self.stear *= 0.9

    def move(self):
        self.last_pos = (self.x,self.y,self.angle)

        self.acceleration += 0.7*self.joystick_y
        self.Xacceleration += 0.7*self.joystick_y*cos(radians(self.angle))
        self.Yacceleration += 0.7*self.joystick_y*sin(radians(self.angle))

        if self.is_player:
            self.turn()

        self.rotate(self.stear/200*self.velocity)
        if self.joystick_x and abs(self.velocity) > 0:
            self.drift += 3

        if self.is_braking:
            self.drift += 1
            if not self.joystick_x:
                self.velocity *= 0.9
        
        self.drift *= 0.96
        self.acceleration *= 0.5
        self.Xacceleration *= 0.5
        self.Yacceleration *= 0.5

        self.velocity += self.acceleration
        self.Xvelocity += self.Xacceleration
        self.Yvelocity += self.Yacceleration

        self.velocity *= 0.96
        self.Xvelocity *= 0.96
        self.Yvelocity *= 0.96

        self.not_drift = 100 - self.drift
        distance = self.velocity*self.not_drift/100/1
        dx = self.Xvelocity*self.drift/100/1.5
        dy = -self.Yvelocity*self.drift/100/1.5
        self.forward(distance)
        self.change_position(dx, dy)


    def back(self):
        self.set_position(self.last_pos[0:2])
        self.set_angle(self.last_pos[2])
    
    def is_next_loop(self,oTrack):
        if oTrack == None:
            return None
        new_tile_id = oTrack.id
        if new_tile_id == 1 and self.tile_id > 2:
            return 1
        elif self.tile_id == 1 and new_tile_id > 2:
            return -1
        return 0
    
    def set_loops(self,oTrack):
        if oTrack == None:
            return
        new_tile_id = oTrack.id
        self.loops += self.is_next_loop(oTrack)
        self.tile_id = new_tile_id