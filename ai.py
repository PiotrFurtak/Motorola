from math import cos, sin, radians
from Car import *

class ai(Car):
    def __init__(self,window,track,coords,image,centre_point,car_id,player):
        Car.__init__(self,window,track,coords,image,centre_point,car_id)
        self.player = player

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
    
    
    def evaluate(self,pixel_values,coords):
        x,y = pixel_values
        match self.car_id:
            case 1:
                value = -0.03*(y)**2+150+x
                if -10 > y > -20:
                    value += 500
                value += self.is_next_loop(self.find_tile(coords)) * 100000

            case 2:
                value = 2*x

                if abs(y) > 20:
                    value -= 100000
                value += self.is_next_loop(self.find_tile(coords)) * 100000
            
            case 3:
                value = x
                if abs(y) > 25:
                    value -= 100000
                value += self.is_next_loop(self.find_tile(coords)) * 100000

                distance = ((self.player.coords[0]-coords[0])**2 + (self.player.coords[1]-coords[1])**2)**(1/2)

                # Omijaj auto, jeśli nie jestem na prawie identycznym progresie wyścigu
                player_pixel_values = self.find_pixel_values(self.player.coords)
                my_pixel_values = self.find_pixel_values(self.coords)
                if player_pixel_values == None or my_pixel_values == None:
                    return value
                if abs(my_pixel_values[0]-player_pixel_values[0]-10) > 10:
                    if distance < 150:
                        value -= 100000
                else:
                    # Jestem tuż obok => Unikalna wartość oznaczająca, że mam się w gracza wpierdolić
                    value = -213700

            case 4:
                player_pixel_values = self.find_pixel_values(self.player.coords)
                if player_pixel_values == None:
                    value = -0.03*(y)**2+150+x
                elif player_pixel_values[1] < y:
                    value = -0.03*(y-player_pixel_values[1])**2+150+x
                else:
                    value = -0.03*(y)**2+150+x
                # if -10 > y > -20:
                #     value += 500
                value += self.is_next_loop(self.find_tile(coords)) * 100000

        return value
    
    def check_values(self,r):
        output = {}
        # for angle in range(-90, 90, 5):
        for angle in range(-180, 181, 5):
            x = r * cos(radians(angle + self.angle)) + self.x
            y = -r * sin(radians(angle + self.angle)) + self.y
            # x,y = self.get_real_point(pygame.mouse.get_pos())
            # x = r * cos(radians(angle)) + x
            # y = -r * sin(radians(angle)) + y
            values = self.find_pixel_values((x, y))
            if values == None:
                continue
            output.setdefault(self.evaluate(values,(x,y)),(angle,(x,y)))
        return output
    

    def enemy_move(self):
        evaluated = {}
        evaluated:dict = self.check_values(40)
        if self.car_id == 2:
            evaluated.update(self.check_values(150))
        if self.car_id == 3:
            evaluated.update(self.check_values(150))
        if self.car_id == 4:
            evaluated.update(self.check_values(100))


        if len(evaluated.keys()) == 0:
            self.stear = 0
            self.joystick_y = -1
            coords_max = (0,0)
        else:

            evaluated_max = max(evaluated.keys())
            angle_max, coords_max = evaluated[evaluated_max]

            self.stear = angle_max

        if -213700 in evaluated.keys():
            # Wpierdol się w gracza
            angle = self.angle
            self.point_at(self.player.coords)
            self.stear = self.angle-angle
            if self.stear < -180:
                self.stear += 360
            elif self.stear > 180:
                self.stear += -360
            self.stear*= 1.5
            self.set_angle(angle)
        self.bonus_conditions()
        self.move()
        self.set_loops()
        self.point.set_position(coords_max)

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