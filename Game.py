import pygame
import sys
from Car import *
from Track import *
pygame.init()

class Game:
    def __init__(self,window):
        self.running = False
        self.WHITE = (255,255,255)
        self.window = window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = window.get_size()
        self.clock = pygame.time.Clock()
        self.player = Car(self.window,(0,-500),pygame.image.load("imgs/red-car.png"),(38,19),is_player=True)
        self.enemy = Car(self.window,(0,-500),pygame.image.load("imgs/red-car.png"),(38,19))
        self.point = Sprite(self.window,(0,0),pygame.image.load("imgs/point.png"),(2,2),0)
        self.pressed_keys = set()

        # self.track = Sprite(self.window,(550,200),pygame.image.load("imgs/track.png"),(450,450))
        # self.track.scale(3)

        # self.border = Sprite(self.window,(550,200),pygame.image.load("imgs/track-border.png"),(450,450))
        # self.border.scale(3)
        turn_img = pygame.image.load("imgs/turn.png")
        forward_img = pygame.image.load("imgs/forward.png")
        self.track = get_level("level-1.txt",window,turn_img,forward_img)
        for oSprite in self.track:
            oSprite.scale(3)
        self.grass = []
        self.GRASS_IMG = pygame.image.load("imgs/grass.jpg")
        for x in range(-2000,2001,self.GRASS_IMG.get_width()):
            for y in range(-2000,2001,self.GRASS_IMG.get_height()):
                self.grass.append(Sprite(self.window,(x,y),self.GRASS_IMG,(0,0)))
        self.game_loop()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                values = self.find_pixel_values(self.get_real_point(event.pos))
                print(values)
                print(500/((abs(values[1]))**(1/2)+10)+values[0])
        self.player.get_pressed_keys(self.pressed_keys)

    def draw(self):

        # Obliczenie relatywnych pozycji x,y i wycentrowanie
        # x = self.WINDOW_WIDTH//2-self.player.x
        # y = self.WINDOW_HEIGHT//2-self.player.y

        x = self.WINDOW_WIDTH//2-self.enemy.x
        y = self.WINDOW_HEIGHT//2-self.enemy.y

        # Narysowanie wszystkich sprite'ów
        for oSprite in self.grass:
            oSprite.draw(x,y)
        for oSprite in self.track:
            oSprite.draw(x,y)
        self.enemy.draw(x,y)
        self.player.draw(x,y)
        self.point.draw(x,y)

    def game_loop(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.window.fill(self.WHITE)

            self.player.move()
            self.enemy_move()
            # if self.player.isColliding(self.border):
            #     self.player.velocity = -self.player.velocity
            #     self.player.back()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)

    def get_real_point(self,coords):
        """Inputs are (x,y) of a point ON A SCREEN
        function returns (x,y) of coords used by program in calculations"""
        x,y = coords
        new_x = x + self.player.x - self.WINDOW_WIDTH//2
        new_y = y + self.player.y - self.WINDOW_HEIGHT//2
        return (new_x,new_y)
    
    def find_pixel_values(self,coords):
        for oSprite in self.track:
            x,y = coords
            if oSprite.x-oSprite.centre_point[0] <= x <= oSprite.x+oSprite.centre_point[0] and oSprite.y-oSprite.centre_point[1] <= y <= oSprite.y+oSprite.centre_point[1]:
                values = oSprite.get_pixel_values(x,y)
                return values[0]+1000*oSprite.id,values[1]
        return None
    
    def enemy_move(self):
        evaluated_max = -10000
        angle_max = 0
        coords_max = (0,0)
        r = 80
        for angle in range(-90,91,3):
            x = r*cos(radians(angle+self.enemy.angle)) + self.enemy.x
            y = -r*sin(radians(angle+self.enemy.angle)) + self.enemy.y
            values = self.find_pixel_values((x,y))
            if values == None:
                continue
            evaluated = 100/((abs(values[1]))**(2)+1)+values[0]
            if evaluated_max < evaluated:
                evaluated_max = evaluated
                angle_max = angle
                coords_max = (x,y)
        if angle_max < 0: self.enemy.stear = -45
        else: self.enemy.stear = 45
        # self.enemy.drift = 0
        self.enemy.joystick_y = 1
        self.enemy.joystick_x = -1
        self.enemy.move()
        self.point.set_position(coords_max)
        # print(angle_max,evaluated_max)