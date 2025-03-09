from math import cos, sin, radians
from Car import *

class ai:
    def __init__(self):
        self.player:Car
        self.enemy:Car
        self.point:Sprite
    def get_real_point(self,coords):
        """Inputs are (x,y) of a point ON A SCREEN
        function returns (x,y) of coords used by program in calculations"""
        x,y = coords
        new_x = x + self.player.x - self.WINDOW_WIDTH//2
        new_y = y + self.player.y - self.WINDOW_HEIGHT//2
        return (new_x,new_y)
    
    def find_pixel_values(self,coords):
        oTrack:Sprite = self.find_tile(coords)
        if oTrack:
            values = oTrack.get_pixel_values(coords)
            return values[0]+1000*oTrack.id,values[1]
        return None
    
    def find_tile(self,coords):
        for oTrack in self.track:
            x,y = coords
            if oTrack.x-oTrack.centre_point[0] <= x <= oTrack.x+oTrack.centre_point[0] and oTrack.y-oTrack.centre_point[1] <= y <= oTrack.y+oTrack.centre_point[1]:
                return oTrack
        return None
    
    def enemy_move(self):
        evaluated_max = -10000
        angle_max = 0
        coords_max = (0, 0)
        r = 45
        for angle in range(-45, 46, 5):
            x = r * cos(radians(angle + self.enemy.angle)) + self.enemy.x
            y = -r * sin(radians(angle + self.enemy.angle)) + self.enemy.y
            values = self.find_pixel_values((x, y))
            if values == None:
                continue
            evaluated = 500 / ((abs(values[1])) ** (1 / 2) + 10) + values[0]
            if evaluated_max < evaluated:
                evaluated_max = evaluated
                angle_max = angle
                coords_max = (x, y)
        self.enemy.stear = angle_max
        self.enemy.joystick_y = 1
        self.enemy.joystick_x = -1
        self.enemy.move()
        self.point.set_position(coords_max)