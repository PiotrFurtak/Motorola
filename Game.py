import pygame
import sys
import random
from Car import *
from Track import *
from Radio import CarRadio  # Zaimportowanie klasy CarRadio
from ai import ai
pygame.init()

class Game(ai):
    def __init__(self, window):
        self.running = False
        self.WHITE = (255, 255, 255)
        self.window = window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = window.get_size()
        self.clock = pygame.time.Clock()
        self.pressed_keys = set()

        self.font = pygame.font.Font(None, 36)  # Czcionka do radia
        self.radio = None  # Na początku nie ma radia

        # self.border = Sprite(self.window,(550,200),pygame.image.load("imgs/track-border.png"),(450,450))
        # self.border.scale(3)
        turn_img = pygame.image.load("imgs/turn.png")
        forward_img = pygame.image.load("imgs/forward.png")
        self.track = get_level("level-1.txt",window,turn_img,forward_img)
        for oTrack in self.track:
            oTrack.scale(3)
        self.grass = []
        self.GRASS_IMG = pygame.image.load("imgs/grass.jpg")
        for x in range(-2000, 2001, self.GRASS_IMG.get_width()):
            for y in range(-2000, 2001, self.GRASS_IMG.get_height()):
                self.grass.append(Sprite(self.window, (x, y), self.GRASS_IMG, (0, 0)))

        self.player = Car(self.window,self.track,(0,-500),pygame.image.load("imgs/red-car.png"),(38,19),is_player=True)
        self.enemy = Car(self.window,self.track,(0,-400),pygame.image.load("imgs/red-car.png"),(38,19))
        self.point = Sprite(self.window,(0,0),pygame.image.load("imgs/point.png"),(2,2),0)

        self.game_loop()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)

                # Przełączanie radia klawiszem R
                if event.key == pygame.K_r:
                    if self.radio:
                        self.radio.toggle_radio()

            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                values = self.find_pixel_values(self.get_real_point(event.pos))
                if values != None:
                    print(values)

        self.player.get_pressed_keys(self.pressed_keys)

    def draw(self):

        # Obliczenie relatywnych pozycji x,y i wycentrowanie
        x = self.WINDOW_WIDTH//2-self.player.x
        y = self.WINDOW_HEIGHT//2-self.player.y


        if pygame.K_1 in self.pressed_keys:
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
        if self.radio:
            self.radio.draw()
        
    def game_loop(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.window.fill(self.WHITE)

            self.player.move()
            self.enemy_move()


            self.player.set_loops() # Uaktualniamy aktualną pętlę gracza
            #
            # Składnia do licznika pętli:
            #
            print(self.player.loops)
            #


            num = random.randint(1, 1)
            if self.radio is None:
                self.radio = CarRadio(self.window, self.font, f"music/music{num}.mp3", self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

            self.draw()
            pygame.display.update()
            self.clock.tick(60)#
