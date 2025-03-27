import pygame

# Początkowo miało być wiele przecisków w menu, ale niestety nie zostało to zrobione

class Button:
    def __init__(self,window,centreCoords,image):
        self.window:pygame.Surface = window
        self.centreCoords = centreCoords
        self.image:pygame.Surface = image
        self.rect = pygame.rect.Rect(self.image.get_rect())
        self.rect.center = (self.centreCoords)

    def isClicked(self,mousePos):
        if self.rect.collidepoint(mousePos):
            return True
        return False
    
    def draw(self):
        self.window.blit(self.image,self.rect.topleft)
