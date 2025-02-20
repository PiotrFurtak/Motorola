from Sprite import Sprite
from math import sqrt,atan,pi

class Turn(Sprite):
    """ type can be for example NE, meaning you approach turn from up(N), and leave a tile from right(E) side """
    # type : (angle, measure point, should_reverse_measured_angle?)
    types = {"NE":{"angle":90,"measure_point":(120,0),"reverse?":False},
                "EN":{"angle":90,"measure_point":(120,0),"reverse?":True},
                "NW":{"angle":180,"measure_point":(0,0),"reverse?":False},
                "WN":{"angle":180,"measure_point":(0,0),"reverse?":True},
                "SE":{"angle":0,"measure_point":(120,120),"reverse?":False},
                "ES":{"angle":0,"measure_point":(120,120),"reverse?":True},
                "SW":{"angle":270,"measure_point":(0,120),"reverse?":False},
                "WS":{"angle":270,"measure_point":(0,120),"reverse?":True}}
    
    def set_pixel_values(measure_point,reverse,height,width):
        values = []
        for y in range(height+1):
            column = []
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

                middle_rate = 64*width/120    # radius of middle of track width
                value_x = angle*180/pi             # Bended geometry
                value_y = radius-middle_rate       # Bended geometry

                column.append((round(value_x),round(value_y)))
            values.append(column)
        return values
    
    values = {}
    for type in types:
        line = types[type]
        values.setdefault(type,set_pixel_values(line["measure_point"],line["reverse?"],130,130))

    def __init__(self,window,coords,image,type,id):
        self.type = type
        angle = self.types[type]["angle"]
        Sprite.__init__(self,window,coords,image,(0,0),angle)
        self.id = id
        self.scale_factor = 1
        self.values = self.values[type]

    def scale(self,factor):
        self.scale_factor = factor
        Sprite.scale(self,factor)

    def get_pixel_values(self,x,y):
        x += -self.x
        y += -self.y
        return self.values[int(y//self.scale_factor)][int(x//self.scale_factor)]

class Forward(Sprite):
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
                    value_y = abs(x-middle_rate)
                elif type[0] == "E":
                    value_x = 130-x
                    value_y = abs(y-middle_rate)
                elif type[0] == "S":
                    value_x = 130-y
                    value_y = abs(x-middle_rate)
                elif type[0] == "W":
                    value_x = x
                    value_y = abs(y-middle_rate)
                

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

        Sprite.__init__(self,window,coords,image,(0,0),angle)
        self.id =id
        self.values = self.all_types_values[type]
        self.scale_factor = 1
    
    def scale(self,factor):
        self.scale_factor = factor
        Sprite.scale(self,factor)

    def get_pixel_values(self,x,y):
        x += -self.x
        y += -self.y
        return self.values[int(y//self.scale_factor)][int(x//self.scale_factor)]

def get_level(file_name,window,turn_image,forward_image):
    file = open("levels/%s"%file_name, "r")
    lines = file.readlines()
    level = []
    for line in lines:
        obj,x,y,obj_type,id = line.split(",")
        x = int(x)
        y = int(y)
        id = int(id)
        if obj.lower() == "turn":
            level.append(Turn(window,(x,y),turn_image,obj_type,id))
        elif obj.lower() == "forward":
            level.append(Forward(window,(x,y),forward_image,obj_type,id))
    file.close()
    return level

def update_level(file_name,level):
    file = open("levels/%s"%file_name, "w")
    for object in level:
        obj = "turn" if type(object) == Turn else "forward"
        x,y = object.coords
        obj_type = object.type
        id = object.id
        file.write(obj+","+str(x)+","+str(y)+","+obj_type+","+str(id)+"\n")
    file.close()

if __name__ == "__main__":
    import pygame
    from time import sleep
    from sys import exit
    pygame.init()
    window = pygame.display.set_mode((800,640))
    turn_img = pygame.image.load("imgs/turn.png")
    forward_img = pygame.image.load("imgs/forward.png")

    level = get_level("level-1.txt",window,turn_img,forward_img)
    for oSprite in level:
        oSprite.scale(3)
    id = len(level)

    obj_type = "NE"
    obj_class = Forward
    img = forward_img
    print(obj_class,obj_type)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                x = x - x%130
                y = y - y%130
                clicked_something = False
                for obj in level:
                    if obj.coords == (x,y):
                        clicked_something = True
                if not clicked_something:
                    id += 1
                    print(obj_class)
                    level.append(obj_class(window,(x,y),img,obj_type,id))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    update_level("level-1.txt",level)
                elif event.key == pygame.K_w:
                    obj_type = "N" + obj_type[1]
                elif event.key == pygame.K_d:
                    obj_type = "E" + obj_type[1]
                elif event.key == pygame.K_s:
                    obj_type = "S" + obj_type[1]
                elif event.key == pygame.K_a:
                    obj_type = "W" + obj_type[1]
                elif event.key == pygame.K_i:
                    obj_type = obj_type[0] + "N"
                elif event.key == pygame.K_l:
                    obj_type = obj_type[0] + "E"
                elif event.key == pygame.K_k:
                    obj_type = obj_type[0] + "S"
                elif event.key == pygame.K_j:
                    obj_type = obj_type[0] + "W"
                elif event.key == pygame.K_0:
                    obj_class = Forward if obj_class == Turn else Turn
                    img = forward_img if obj_class == Forward else turn_img
                print(obj_class,obj_type)

        window.fill("Black")

        for obj in level:
            obj.draw()
        pygame.display.update()
        sleep(0.01)