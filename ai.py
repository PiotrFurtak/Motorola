from math import cos, sin, radians
from Car import *

class ai:
    def __init__(self):
        self.player:Car
        self.enemies:tuple[Car]
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
    
    def evaluate(self,x,y,oCar):
        oCar:Car
        match oCar.ai_id:
            case 1:
                value = -0.03*(y)**2+150+x
                if -10 > y > -25:
                    value += 1000
                value += oCar.is_next_loop(self.find_tile((x,y))) * 100000

            case 2:
                value = 2*x

                if abs(y) > 20:
                    value -= 100000
                value += oCar.is_next_loop(self.find_tile((x,y))) * 100000
            
            case 3:
                value = 0
            
            case 4:
                value = 0

        return value
    
    def check_values(self,r,enemy):
        output = {}
        for angle in range(-90, 90, 5):
        # for angle in range(-180, 181, 5):
            x = r * cos(radians(angle + enemy.angle)) + enemy.x
            y = -r * sin(radians(angle + enemy.angle)) + enemy.y
            # x,y = self.get_real_point(pygame.mouse.get_pos())
            # x = r * cos(radians(angle)) + x
            # y = -r * sin(radians(angle)) + y
            values = self.find_pixel_values((x, y))
            if values == None:
                continue
            output.setdefault(self.evaluate(values[0],values[1],enemy),(angle,(x,y)))
        return output


    def enemy_move(self):
        for enemy in self.enemies:
            evaluated:dict = self.check_values(40,enemy)
            if enemy.ai_id == 2:
                evaluated.update(self.check_values(150,enemy))
            evaluated_max = max(evaluated.keys())
            angle_max, coords_max = evaluated[evaluated_max]

            enemy.stear = angle_max

            enemy.move()
            enemy.set_loops()
            if enemy.ai_id == 2:
                self.point.set_position(coords_max)