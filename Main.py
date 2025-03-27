import pygame
from sys import exit
from Game import Game
from Button import Button
WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_desktop_sizes()[0]
WINDOW_HEIGHT -= 10
WINDOW_WIDTH -= 10
window = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
FONT = pygame.font.SysFont("bahnschrift", 36)
BUTTON = pygame.image.load("imgs/start-button.png")
BUTTON = pygame.transform.scale(BUTTON,(100,50))
startButton = Button(window,(WINDOW_WIDTH//2,WINDOW_HEIGHT//1.3),BUTTON)

car_names = {0:"Gracz",1:"Bot1 ",2:"Bot2 ",3:"Bot3 ",4:"Bot4 "}

def start_game(): 
    oGame = Game(window) # Rozpoczynamy grę
    scores = oGame.scores # Patrzymy na wyniki tej gry
    return scores # I zwracamy

def draw_table(scores):
    window.fill((0,0,0))
    for i, (oCar, time,best_lap_time) in enumerate(scores): # Wypisujemy miejsce, nazwę auta, czas i najlepszy czas okrążenia
        string = f"Miejsce {i+1}. {car_names[oCar.car_id]} - Czas przejazdu: "+"{0:.3f}".format(time)+", Najszybsze okrążenie: "+"{0:.3f}".format(best_lap_time)
        text = FONT.render(string,True,(242, 245, 47))
        window.blit(text,(WINDOW_WIDTH//2-text.get_width()//2,i*50+100)) 
    startButton.draw() # A na końcu rysujemy przycisk do włączenia gry znowu

def main_loop(): # Pętla główna aplikacji
    startButton.draw()
    space = FONT.render("(Spacja - drift, \"K\" - rozlanie oleju)",True,(242, 245, 47)) # Wypisujemy informację dla gracza
    x = WINDOW_WIDTH//2 - space.get_width()//2
    y = WINDOW_HEIGHT//9*8
    window.blit(space,(x,y))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Wychodzimy z aplikacji po naciśnięciu X
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Sprawdzamy czy wcisnęliśmy lewy przycisk myszy
                    if startButton.isClicked(event.pos): # Sprawdzamy czy myszka najechała na przycisk
                        scores = start_game() # Zaczynamy grę
                        # Następna linijka wykona się dopiero po zakończeniu lub wyjściu z wyścigu
                        if scores:
                            draw_table(scores) # Rysujemy tabelę wyników

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Wychodzimy również klawiszem esc
                    pygame.quit()
                    exit()
        
        pygame.display.update() # Uaktualniamy ekran

main_loop() # Po uruchomieniu pliku, aplikacja ma zacząć działać