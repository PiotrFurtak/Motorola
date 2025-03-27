import pygame
from math import sin,cos,radians,atan,degrees

class Sprite:
    def __init__(self,window,coords,image,centre_point,angle=0,is_player=False):
        self.window = window
        self.WINDOW_WIDTH = self.window.get_width()
        self.WINDOW_HEIGHT = self.window.get_height()
        self.coords = coords
        self.x,self.y = coords
        self.absolute_x,self.absolute_y = self.coords
        self.angle = angle
        self.base_img = image
        self.mask = pygame.mask.from_surface(self.base_img)
        self.centre_point = centre_point
        self.width = image.get_width()
        self.height = image.get_height()
        self.vector_to_middle = [self.width/2-self.centre_point[0],self.height/2-self.centre_point[1]]
        self.scale_factor = 1
        self.set_angle(angle)
        self.is_player = is_player

    def change_position(self,x,y):
        self.x += x
        self.y += y
        self.coords = (self.x,self.y)
        self.reset_absolute_values()

    def set_position(self,coords):
        self.coords = coords
        self.x,self.y = self.coords
        self.reset_absolute_values()

    def forward(self,distance):
        x = distance * cos(radians(self.angle))
        y = distance * sin(radians(self.angle))
        self.change_position(x,-y)

    def rotate(self,angle_deg):
        angle_deg %= 360
        x,y = self.vector_to_middle[0],self.vector_to_middle[1]
        new_x = x*cos(radians(angle_deg)) - y*sin(radians(angle_deg))
        new_y = x*sin(radians(angle_deg)) + y*cos(radians(angle_deg))
        self.vector_to_middle = [new_x,new_y]
        self.angle = (self.angle+angle_deg)%360
        self.image = pygame.transform.rotate(self.base_img,self.angle)
        self.scale_by(self.scale_factor)
        
        
    def set_angle(self,angle_deg):
        dangle = angle_deg - self.angle
        self.rotate(dangle)

    def point_at(self,coords):
        dx = coords[0] - self.x
        dy = coords[1] - self.y
        if dx == 0:
            if dy < 0:
                angle = 90
            else:
                angle = 270
        elif dx > 0:
            angle = degrees(atan(-dy/dx))
        else:
            angle = 180 + degrees(atan(-dy/dx))
        self.rotate(angle-self.angle)

    def draw(self, relative_x=0, relative_y=0):
        self.window.blit(self.image, (self.absolute_x + relative_x, self.absolute_y + relative_y))

    def isColliding(self,oSprite):
        offset = (self.absolute_x-oSprite.absolute_x, self.absolute_y-oSprite.absolute_y)
        if oSprite.mask.overlap(self.mask,offset):
            return True
        return False

    def reset_absolute_values(self):
        self.width,self.height = self.image.get_size()
        self.absolute_x = self.x + self.vector_to_middle[0] - self.width/2
        self.absolute_y = self.y - self.vector_to_middle[1] - self.height/2
        
        

    def scale_by(self,factor):
        self.scale_factor = factor
        self.image = pygame.transform.scale_by(self.image,factor)
        self.mask = pygame.mask.from_surface(self.image)
        x,y = self.centre_point
        self.centre_point = factor*x, factor*y
        x,y = self.vector_to_middle
        self.vector_to_middle = (x*factor, y*factor)
        self.reset_absolute_values()
        
    def move(self):
        pass
