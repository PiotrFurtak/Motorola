from Sprite import Sprite
from math import cos,sin,radians,copysign
from time import time
import pygame

class Car(Sprite):
    def __init__(self,window,track,coords,image,centre_point,angle,car_id):
        self.car_id = car_id
        Sprite.__init__(self,window,coords,image,centre_point,angle,is_player=car_id==0)
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
        self.laps = 0
        self.laps_times = [time()]
        self.best_lap_time = 1000000
        self.point = Sprite(self.window,(0,0),pygame.image.load("imgs/point.png"),(2,2),0)
        self.oil_cooldown = 0
        self.oil_coords = (0,0)
        self.oil_radius = 0
        self.oiled_time = 0
        self.hitbox = Sprite(self.window,coords,pygame.image.load("imgs/car-hitbox.png"),centre_point)
        self.hitbox.scale_by(1/6)

    def draw(self,x,y):
        if self.oil_radius > 0:
            pygame.draw.circle(self.window,(0,0,0),(x+self.oil_coords[0],y+self.oil_coords[1]),self.oil_radius)
            if self.oil_radius < 75:
                self.oil_radius += 1
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

        if self.oil_cooldown > 0:
            self.oil_cooldown += -1
        if pygame.K_k in self.pressed_keys:
            self.spill_oil()

    def spill_oil(self):
        if self.oil_cooldown > 0:
            return
        self.oil_coords = self.x,self.y
        self.oil_radius = 1
        self.oil_cooldown = 60*15

    def check_oil_collision(self,player):
        if player.oil_radius == 0:
            return False
        oil = pygame.surface.Surface((player.oil_radius*2,player.oil_radius*2))
        pygame.draw.circle(oil,(0,0,0),(player.oil_radius,player.oil_radius),player.oil_radius)
        mask = pygame.mask.from_surface(oil)
        if self.mask.overlap(mask,(self.x-player.oil_coords[0],self.y-player.oil_coords[1])):
            self.oiled_time = 60*3
            return True
        return False
    
    def isColliding(self,oSprite):
        x,y = self.coords
        self.hitbox.set_position((x/6,y/6))
        self.hitbox.set_angle(self.angle)
        return Sprite.isColliding(self.hitbox,oSprite.hitbox)

    def turn(self):
        if self.joystick_x == 0:
            self.stear *= 0.3
        self.stear += 4 * self.joystick_x
        self.stear *= 0.9

    def move(self):
        if self.oiled_time > 0: 
            self.oiled_time += -1
            self.drift = 95
            self.Xacceleration = 0
            self.Yacceleration = 0
            # self.stear *= 1.5
        self.last_pos = (self.x,self.y,self.angle)

        self.acceleration += 0.7*self.joystick_y
        self.Xacceleration += 0.7*self.joystick_y*cos(radians(self.angle))
        self.Yacceleration += 0.7*self.joystick_y*sin(radians(self.angle))

        if self.is_player:
            self.turn()

        self.rotate(self.stear/200*self.velocity)
        if self.joystick_x and abs(self.velocity) > 0:
            self.drift += 1

        if self.is_braking:
            self.drift += 3
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
        if not self.oiled_time:
            self.Xvelocity *= 0.96
            self.Yvelocity *= 0.96
        else:
            self.Xvelocity *= 0.98
            self.Yvelocity *= 0.98

        self.not_drift = 100 - self.drift
        distance = self.velocity*self.not_drift/100/1
        dx = self.Xvelocity*self.drift/100/1.5
        dy = -self.Yvelocity*self.drift/100/1.5
        self.forward(distance)
        self.change_position(dx, dy)

    def back(self):
        self.set_position(self.last_pos[0:2])
        self.set_angle(self.last_pos[2])
    
    def is_next_lap(self,oTrack):
        if oTrack == None:
            return 0
        new_tile_id = oTrack.id
        if new_tile_id < 3 and self.tile_id > 10:
            if self.laps != len(self.laps_times)-1:
                return 1
            self.laps_times.append(time())
            if self.laps_times[-1] - self.laps_times[-2] < self.best_lap_time:
                self.best_lap_time = self.laps_times[-1] - self.laps_times[-2]
            return 1
        elif self.tile_id < 3 and new_tile_id > 10:
            return -1
        return 0
    
    def set_laps(self):
        oTrack = self.find_tile(self.coords)
        if oTrack == None:
            return
        new_tile_id = oTrack.id
        self.laps += self.is_next_lap(oTrack)
        self.tile_id = new_tile_id

    def find_tile(self,coords):
        for oTrack in self.track:
            x,y = coords
            if oTrack.x-oTrack.centre_point[0] <= x <= oTrack.x+oTrack.centre_point[0] and oTrack.y-oTrack.centre_point[1] <= y <= oTrack.y+oTrack.centre_point[1]:
                return oTrack
        return None