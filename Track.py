from Sprite import Sprite
from math import sqrt,atan,pi
import pygame

class Turn(Sprite):
    """ type can be for example NE, meaning you approach turn from up(N), and leave a tile from right(E) side """
    types = {"NE":{"angle":90,"measure_point":(130,0),"reverse?":False,"direction":"L"},  # Pierwsza litera typu oznacza skąd wjeżdżamy na pole
                "EN":{"angle":90,"measure_point":(130,0),"reverse?":True,"direction":"P"},# a druga oznacza skąd wyjeżdżamy z pola
                "NW":{"angle":180,"measure_point":(0,0),"reverse?":False,"direction":"P"},
                "WN":{"angle":180,"measure_point":(0,0),"reverse?":True,"direction":"L"},
                "SE":{"angle":0,"measure_point":(130,130),"reverse?":False,"direction":"P"},
                "ES":{"angle":0,"measure_point":(130,130),"reverse?":True,"direction":"L"},
                "SW":{"angle":270,"measure_point":(0,130),"reverse?":False,"direction":"L"},
                "WS":{"angle":270,"measure_point":(0,130),"reverse?":True,"direction":"P"}}
    
    def set_pixel_values(measure_point,reverse,height,width,direction): # Każdy piksel ma swoją "zakrzywioną geometryczną wartość"
        values = []                                           # x oznacza odległość tzn. im większy x tym dalej pojechaliśmy od staru
        for y in range(height+1):                             # y oznacza wychylenie na lewo-prawo
            column = []                                       # W zależności od typu zakrętu będzie się zmieniać sposób liczenia x i y
            for x in range(width+1):
                dx = measure_point[0] - x
                dy = measure_point[1] - y
                radius = sqrt(dx**2 + dy**2)
                if dx != 0:
                    angle = abs(atan(dy/dx))
                else:
                    angle = pi/2
                
                if reverse:
                    angle = pi/2 - angle

                middle_rate = 65*width/130
                value_x = angle*180/pi
                value_y = radius-middle_rate
                if direction == "P": value_y *= -1
                column.append((value_x,value_y))
            values.append(column)
        return values
    
    values = {}
    for type in types:
        line = types[type]
        values.setdefault(type,set_pixel_values(line["measure_point"],line["reverse?"],130,130,line["direction"]))

    def __init__(self,window,coords,image,type,id):
        self.type = type
        angle = self.types[type]["angle"]
        Sprite.__init__(self,window,coords,image,(65,65),angle)
        self.hitbox = Sprite(self.window,coords,pygame.image.load("imgs/turn-hitbox.png"),(65,65),angle) # Każde pole ma osobno dostęp do swojego hitboxa
        self.id = id # Oraz ma swoje id
        
        self.values = self.values[type] # Oraz swoje wartości x i y

    def scale(self,factor): # Skalujemy pole toru normalnie, ale hitboxa specjalnie nie ruszamy, żeby nie spadała wydajność
        self.scale_factor = factor
        self.hitbox.set_position((self.x/factor,self.y/factor)) # Zamiast tego stosujemy jednokładność względem punktu (0,0)
        Sprite.scale_by(self,factor)                            # i będziemy zmniejszać auto do proporcjonalnej wielkości

    def get_pixel_values(self,coords): # Podajemy zwykłe współrzędne i funkcja zwraca te wartości swoje specjalne x,y
        x,y = coords
        x += self.centre_point[0] - self.x
        y += self.centre_point[1] - self.y
        return self.values[int(y//self.scale_factor)][int(x//self.scale_factor)]

class Forward(Sprite):             # Tutaj generalnie wszystko będzie analogicznie
    types = {"WE":{"angle":0},
            "EW":{"angle":180},
            "SN":{"angle":90},
            "NS":{"angle":270}}
    
    def set_pixel_values(type,width,height):
        values = []
        for y in range(height+1):
            column = []
            for x in range(width+1):
                
                middle_rate = width/2

                if type[0] == "N":
                    value_x = y
                    value_y = -x+middle_rate
                elif type[0] == "E":
                    value_x = 130-x
                    value_y = -y+middle_rate
                elif type[0] == "S":
                    value_x = 130-y
                    value_y = x-middle_rate
                elif type[0] == "W":
                    value_x = x
                    value_y = y-middle_rate
                

                column.append((value_x,value_y))
            values.append(column)
        return values

    all_types_values = {}

    for type in types:
        all_types_values.setdefault(type,set_pixel_values(type,130,130))

    def __init__(self,window,coords,image,type,id):
        self.type = type
        """ type can be for example NS meaning we approach tile from up and go down """
        angle = self.types[type]["angle"]

        Sprite.__init__(self,window,coords,image,(65,65),angle)
        self.hitbox = Sprite(self.window,coords,pygame.image.load("imgs/forward-hitbox.png"),(65,65),angle)
        self.id =id
        self.values = self.all_types_values[type]
        
    
    def scale(self,factor):
        self.scale_factor = factor
        self.hitbox.set_position((self.x/factor,self.y/factor))
        Sprite.scale_by(self,factor)

    def get_pixel_values(self,coords):
        x,y = coords
        x += self.centre_point[0] - self.x
        y += self.centre_point[1] - self.y
        return self.values[int(y//self.scale_factor)][int(x//self.scale_factor)]

def get_level(file_name,window,turn_image,forward_image): # Czytamy poziom z odpowiedniego pliku .txt i zwracamy listę z polami toru
    file = open("levels/%s"%file_name, "r")
    lines = file.readlines()
    level = []
    for line in lines:
        obj,x,y,obj_type,id = line.split(",") # Interesuje nas klasa (zakręt/prosta), koordynaty, typ (np. "NW") i id
        x = int(x)
        y = int(y)
        id = int(id)
        if obj.lower() == "turn":
            level.append(Turn(window,(x,y),turn_image,obj_type,id))
        elif obj.lower() == "forward":
            level.append(Forward(window,(x,y),forward_image,obj_type,id))
    file.close()
    return level # Zwracamy listę z gotowymi obiektami
#
# Kiedyś był tu też "kreator poziomu", ale był średnio intuicyjny oraz nie był priorytetem, dlatego został usunięty
#