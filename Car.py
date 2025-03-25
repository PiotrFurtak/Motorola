from Sprite import Sprite
from math import cos,sin,radians,copysign
import pygame

class Car(Sprite):
    def __init__(self,window,track,coords,image,centre_point,car_id,player=None):
        self.car_id = car_id
        Sprite.__init__(self,window,coords,image,centre_point,0,is_player=car_id==0)
        self.track = track
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
        self.point = Sprite(self.window,(0,0),pygame.image.load("imgs/point.png"),(2,2),0)
        self.player = player

    def draw(self,x,y):
        Sprite.draw(self,x,y)
        # self.point.draw(x,y)

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
        self.bonus_conditions()

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

    def bonus_conditions(self):
        if self.joystick_y == -1: return
        if not self.is_player: self.joystick_y = 0
        match self.car_id:
            case 1:
                if self.velocity < 15:
                    self.joystick_y = 1
            case 2:
                speed_limit = 7 if abs(self.stear) > 10 else 100
                if self.velocity < speed_limit:
                    self.acceleration += 0.25
                    self.joystick_y = 1
            case 3:
                speed_limit = 7 if abs(self.stear) > 10 else 100
                if self.velocity < speed_limit:
                    self.acceleration += 0.25
                    self.joystick_y = 1
            case 4:
                speed_limit = 15

                player_pixel_values = self.find_pixel_values(self.player.coords)
                my_pixel_values = self.find_pixel_values(self.coords)

                if None not in (player_pixel_values, my_pixel_values):
                    if my_pixel_values[0] - player_pixel_values[0] > 1000:
                        speed_limit = 10
                        
                if self.velocity < speed_limit:
                    self.joystick_y = 1

    def back(self):
        self.set_position(self.last_pos[0:2])
        self.set_angle(self.last_pos[2])
    
    def is_next_loop(self,oTrack):
        if oTrack == None:
            return 0
        new_tile_id = oTrack.id
        if new_tile_id < 3 and self.tile_id > 10:
            return 1
        elif self.tile_id < 3 and new_tile_id > 10:
            return -1
        return 0
    
    def set_loops(self):
        oTrack = self.find_tile(self.coords)
        if oTrack == None:
            return
        new_tile_id = oTrack.id
        self.loops += self.is_next_loop(oTrack)
        self.tile_id = new_tile_id

    def find_tile(self,coords):
        for oTrack in self.track:
            x,y = coords
            if oTrack.x-oTrack.centre_point[0] <= x <= oTrack.x+oTrack.centre_point[0] and oTrack.y-oTrack.centre_point[1] <= y <= oTrack.y+oTrack.centre_point[1]:
                return oTrack
        return None