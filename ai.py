from math import cos, sin, radians, copysign
from Car import *

# 
# No i zaczynamy zabawę...
#

class ai(Car):
    def __init__(self,window,track,coords,image,angle,centre_point,car_id,player):
        Car.__init__(self,window,track,coords,image,angle,centre_point,car_id)
        self.player = player
        self.already_won = False

    def get_real_point(self,coords): # Z powodu przesuwania kamery, potrzebna jest funkcja, która punkt na ekranie
        # przekształci na odpowiedni wirtualny punkt w świecie gry.
        # Ta funkcja była kluczzowa w debugowaniu, bo można było kliknąć na ekran myszką i ona zwracała koordynaty w grze
        """Inputs are (x,y) of a point ON A SCREEN
        function returns (x,y) of coords used by program in calculations"""
        x,y = coords
        new_x = x + self.player.x - self.WINDOW_WIDTH//2
        new_y = y + self.player.y - self.WINDOW_HEIGHT//2
        return (new_x,new_y)
    
    def find_pixel_values(self,coords): # Dla danego piksela w grze, zwróć wartości x,y "Zakrzywionej geometrii"
        oTrack:Sprite = self.find_tile(coords)
        if oTrack:
            values = oTrack.get_pixel_values(coords)
            return values[0]+1000*oTrack.id,values[1]
        return None
    
    
    def evaluate(self,pixel_values,coords): # Każde auto w inny sposób ocenia, jak bardzo opłaca się dany piksel
        x,y = pixel_values
        match self.car_id:
            case 1:    # Po prostu patrzymy na progres wyścigu i żeby nie wychylać się za bardzo od środka
                value = 2*x

                if abs(y) > 20: 
                    value -= 100000
                value += self.is_next_lap(self.find_tile(coords)) * 100000 

            case 2:  # Jedziemy centralnie środkiem i tyle
                value = -0.03*(y)**2+150+x
                if -10 > y > -20:
                    value += 500
                value += self.is_next_lap(self.find_tile(coords)) * 100000
            
            case 3:
                value = x # Robimy to co auto 1
                if abs(y) > 25:
                    value -= 100000
                value += self.is_next_lap(self.find_tile(coords)) * 100000

                distance = ((self.player.coords[0]-coords[0])**2 + (self.player.coords[1]-coords[1])**2)**(1/2)

                player_pixel_values = self.find_pixel_values(self.player.coords)
                my_pixel_values = self.find_pixel_values(self.coords)
                if player_pixel_values == None or my_pixel_values == None:
                    return value
                if abs(my_pixel_values[0]-player_pixel_values[0]-10) > 10: 
                    if distance < 150:
                    # Omijaj auto, jeśli nie jestem na prawie identycznym progresie wyścigu
                        value -= 100000
                else:
                    # Jestem tuż obok => Unikalna wartość oznaczająca, że mam się w gracza wpierdolić
                    value = -213700

            case 4:
                player_pixel_values = self.find_pixel_values(self.player.coords)
                if player_pixel_values == None:
                    value = -0.03*(y)**2+150+x
                elif player_pixel_values[0]+20 < x:
                    value = -0.03*(y-player_pixel_values[1])**2+150+x # Jak jest przed graczem, to jedź centralnie przed nim
                else:
                    value = -0.03*(y)**2+150+x # W przeciwnym razie jedź środkiem
                    
                value += self.is_next_lap(self.find_tile(coords)) * 100000
                if abs(y) > 30: value -= 200000 # No i spróbuj nie wpieprzać się w bariery...

        return value
    
    def check_values(self,r): # Wykonujemy kolisty "skan" pikselów wokół auta, żeby zobaczyć który jest najbardziej opłacalny
        output = {}           # czyli w którą stronę trzeba jechać
        for angle in range(-180, 181, 5):
            x = r * cos(radians(angle + self.angle)) + self.x
            y = -r * sin(radians(angle + self.angle)) + self.y
            values = self.find_pixel_values((x, y))
            if values == None:
                continue
            output.setdefault(self.evaluate(values,(x,y)),(angle,(x,y))) # Zapisujemy wartości w słowniku
        return output
    

    def enemy_move(self): # Oceniamy w którą stronę i poruszamy boty
        evaluated = {}
        evaluated:dict = self.check_values(40) # Domyślnie każde auto wykonuje skan o promieniu 40
        if self.car_id == 1:                         #
            evaluated.update(self.check_values(150)) # Inne wartości skanu powodują, że niektóre auta jeżdżą naturalniej
        if self.car_id == 3:                         # i "tak jak powinny"
            evaluated.update(self.check_values(150)) #
        if self.car_id == 4:                         #
            evaluated.update(self.check_values(100)) #


        if len(evaluated.keys()) == 0:
            self.stear = 0
            self.joystick_y = -1
            coords_max = (0,0)
        else:

            evaluated_max = max(evaluated.keys())
            angle_max, coords_max = evaluated[evaluated_max] # Koordynaty maksymalne służyły do debugowania i ulepszania algorytmów botów
            # Każdy bot rysował kropkę, dzięki czemu widać było "Proces myślowy" bota. W połączeniu z klikaniem w ekran i zwracaniem wartości
            # "zakrzywionej geometrii" można było skorygować algorytmy

            self.stear = angle_max
            if self.car_id == 4:
                self.stear *= 1.3 # Bot4 ma być bardziej zwrotny

        if -213700 in evaluated.keys(): # Specjalna wartość dla bota3
            # Wpierdol się w gracza
            angle = self.angle
            self.point_at(self.player.coords) # Generalnie szuka kąta -180~180 dla którego będzie skierowany w stronę gracza
            self.stear = self.angle-angle
            if self.stear < -180:
                self.stear += 360
            elif self.stear > 180:
                self.stear += -360
            self.stear*= 1.5         # Losowo daje to lepszy efekt
            self.set_angle(angle)
        self.bonus_conditions() # Każde auto ma jakieś swoje specjalne warunki jazdy
        self.move()             # Inicjuj ruch
        self.set_laps()         # Uaktualnij okrążenia

    def bonus_conditions(self):
        if self.joystick_y == -1: return
        if not self.is_player: self.joystick_y = 0
        match self.car_id:
            case 1:
                speed_limit = 7 if abs(self.stear) > 10 else 100 # Jeśli skręt mamy prawie prosto, to prędkość jest praktycznie bez limitu
                if self.velocity < speed_limit:
                    if not self.already_won: self.acceleration += 0.25 # Dodatkowo zwiększamy przyspieszenie
                    self.joystick_y = 1
            case 2:
                if self.velocity < 15:
                    self.joystick_y = 1
            case 3:
                speed_limit = 7 if abs(self.stear) > 10 else 100
                if self.velocity < speed_limit:
                    if not self.already_won: self.acceleration += 0.25
                    self.joystick_y = 1
            case 4:
                speed_limit = 13
                x1,x2 = self.find_pixel_values(self.coords)[0], self.find_pixel_values(self.player.coords)[0]
                if x1 - 30 < x2:
                    speed_limit = 18 # Jeśli jest za graczem lub tuż przed, to goń/nie daj się wyprzedzić
                    self.acceleration += 0.15
                if self.velocity < speed_limit:
                    self.joystick_y = 1
        if self.already_won: self.joystick_y = 0 # Zatrzymuj jeśli auto skończyło wyścig