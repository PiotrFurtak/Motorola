import pygame
import sys
from Car import *
pygame.init()
BLACK = (0,0,0)
GREEN = (10,100,30)
WHITE = (255,255,255)
WINDOW_WIDTH, WINDOW_HEIGHT = (640,480)

# Chcemy mieć pewność, że przekątna okna jest mniejsza lub równa niż bok bufora, żeby nie było dziur w rogach
DIAGONAL = (WINDOW_HEIGHT**2 + WINDOW_WIDTH**2)**0.5
DIAGONAL = int(DIAGONAL) + 1
buffer = pygame.surface.Surface((DIAGONAL,DIAGONAL))
window = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
clock = pygame.time.Clock()
player = Car(buffer,(100,150),pygame.image.load("imgs/red-car.png"),(48,18),is_player=True)
pressed_keys = set()

track = Sprite(buffer,(550,200),pygame.image.load("imgs/track.png"),(450,450))
track.scale(2)

border = Sprite(buffer,(550,200),pygame.image.load("imgs/track-border.png"),(450,450))
border.scale(2)

grass = []
GRASS_IMG = pygame.image.load("imgs/grass.jpg")
for x in range(-2000,2001,GRASS_IMG.get_width()):
    for y in range(-2000,2001,GRASS_IMG.get_height()):
        grass.append(Sprite(buffer,(x,y),GRASS_IMG,(0,0)))

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            pressed_keys.add(event.key)
        elif event.type == pygame.KEYUP:
            pressed_keys.discard(event.key)

    player.get_pressed_keys(pressed_keys)

def draw():

    # Umieść wszystkie sprite'y na buforze
    for oSprite in grass:
        oSprite.draw(DIAGONAL//2-player.x,DIAGONAL//2-player.y)
    track.draw(DIAGONAL//2-player.x,DIAGONAL//2-player.y)
    player.draw(DIAGONAL//2-player.x,DIAGONAL//2-player.y)
    # player.oFrontWheels.draw(DIAGONAL//2-player.x,DIAGONAL//2-player.y)

    # Obróć bufor
    rotated = pygame.transform.rotate(buffer,(-player.angle+90))
    center = rotated.get_rect().center
    # Wyświetl bufor
    window.blit(rotated,(WINDOW_WIDTH//2-center[0],WINDOW_HEIGHT//2-center[1]))
    


def game_loop():
    while True:
        handle_events()
        window.fill(WHITE)

        player.move()
        if player.isColliding(border):
            player.velocity = -player.velocity
            player.back()
        
        draw()
        pygame.display.update()
        clock.tick(60)
game_loop()