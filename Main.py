import pygame
from Game import Game
WINDOW_WIDTH, WINDOW_HEIGHT = (640,480)
window = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
oGame = Game(window)
window.fill((0,0,0))
pygame.display.update()
print("Hello world!")