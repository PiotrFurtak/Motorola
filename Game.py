import pygame
import sys
from Car import *
pygame.init()

class Game:
    def __init__(self,window):
        self.running = False
        self.WHITE = (255,255,255)
        self.window = window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = window.get_size()
        # Chcemy mieć pewność, że przekątna okna jest mniejsza lub równa niż bok bufora, żeby nie było dziur w rogach
        self.DIAGONAL = (self.WINDOW_HEIGHT**2 + self.WINDOW_WIDTH**2)**0.5
        self.DIAGONAL = int(self.DIAGONAL) + 1

        self.buffer = pygame.surface.Surface((self.DIAGONAL,self.DIAGONAL))
        self.clock = pygame.time.Clock()
        self.player = Car(self.buffer,(100,150),pygame.image.load("imgs/red-car.png"),(48,18),is_player=True)
        self.pressed_keys = set()

        self.track = Sprite(self.buffer,(550,200),pygame.image.load("imgs/track.png"),(450,450))
        self.track.scale(2)

        self.border = Sprite(self.buffer,(550,200),pygame.image.load("imgs/track-border.png"),(450,450))
        self.border.scale(2)

        self.grass = []
        self.GRASS_IMG = pygame.image.load("imgs/grass.jpg")
        for x in range(-2000,2001,self.GRASS_IMG.get_width()):
            for y in range(-2000,2001,self.GRASS_IMG.get_height()):
                self.grass.append(Sprite(self.buffer,(x,y),self.GRASS_IMG,(0,0)))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)

        self.player.get_pressed_keys(self.pressed_keys)

    def draw(self):

        # Umieść wszystkie sprite'y na buforze
        for oSprite in self.grass:
            oSprite.draw(self.DIAGONAL//2-self.player.x,self.DIAGONAL//2-self.player.y)
        self.track.draw(self.DIAGONAL//2-self.player.x,self.DIAGONAL//2-self.player.y)
        self.player.draw(self.DIAGONAL//2-self.player.x,self.DIAGONAL//2-self.player.y)
        # self.player.oFrontWheels.draw(self.DIAGONAL//2-self.player.x,self.DIAGONAL//2-self.player.y)

        # Obróć bufor
        rotated = pygame.transform.rotate(self.buffer,(-self.player.angle+90))
        center = rotated.get_rect().center
        # Wyświetl bufor
        self.window.blit(rotated,(self.WINDOW_WIDTH//2-center[0],self.WINDOW_HEIGHT//2-center[1]))
        


    def game_loop(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.window.fill(self.WHITE)

            self.player.move()
            if self.player.isColliding(self.border):
                self.player.velocity = -self.player.velocity
                self.player.back()
            
            self.draw()
            pygame.display.update()
            self.clock.tick(60)