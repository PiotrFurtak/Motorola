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
    scores = oGame.scores
    return scores
def draw_table(scores):
    window.fill((0,0,0))
    for oCar, time,best_lap_time in scores:
        print(oCar.car_id,round(time,3),round(best_lap_time,3))

def main_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if startButton.isClicked(event.pos):
                        scores = start_game()
                        if scores:
                            draw_table(scores)
                            # Tu ma być przycisk do pominięcia ekranu

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        
        window.fill((0,0,0))
        startButton.draw()
        pygame.display.update()

main_loop()