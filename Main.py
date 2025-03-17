import pygame
from sys import exit
from Game import Game
from Button import Button
# WINDOW_WIDTH, WINDOW_HEIGHT = (640,480)
WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_desktop_sizes()[0]
# WINDOW_WIDTH -= 10
# WINDOW_HEIGHT -= 10
window = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
listOfButtons = []

BUTTON = pygame.image.load("imgs/start-button.png")
BUTTON = pygame.transform.scale(BUTTON,(100,50))
startButton = Button(window,(WINDOW_WIDTH//2,WINDOW_HEIGHT//2),BUTTON)

def start_game():
    oGame = Game(window)
start_game()
def main_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Zakończenie działania programu
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Lewy przycisk myszy
                if event.button == 1:
                    # Sprawdź czy najechano na jakiś przycisk
                    if startButton.isClicked(event.pos):
                        # Uruchom grę
                        start_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        
        window.fill((0,0,0))
        startButton.draw()
        pygame.display.update()

main_loop()