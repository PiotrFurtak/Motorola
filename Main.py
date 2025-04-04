import pygame
from sys import exit
from Game import Game
from Button import Button
WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.get_desktop_sizes()[0]
window = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
FONT = pygame.font.SysFont("bahnschrift", 36)
BUTTON = pygame.image.load("imgs/start-button.png")
BUTTON = pygame.transform.scale(BUTTON,(400,180))
startButton = Button(window,(WINDOW_WIDTH//2,WINDOW_HEIGHT//1.3),BUTTON)
LEVEL_BUTTONS_IMG = [pygame.image.load(f"imgs/level-{i+1}-button.png") for i in range(3)]  # Ustaw zdjęcia
level_buttons = [Button(window,(WINDOW_WIDTH//2-400+400*i,WINDOW_HEIGHT//1.2),LEVEL_BUTTONS_IMG[i]) for i in range(3)] # Definicja obiektów
chosen_level = 0  # ZERO OZNACZA BRAK WYBRANEGO POZIOMU
player_nick = ""
scores = []


def start_game(): 
    oGame = Game(window,player_nick,chosen_level) # Rozpoczynamy grę
    scores = oGame.scores # Patrzymy na wyniki tej gry
    return scores # I zwracamy

def draw_table(scores):
    car_names = {0:player_nick,1:"Bot1 ",2:"Bot2 ",3:"Bot3 ",4:"Bot4 "}
    window.fill((0,0,0))
    for i, (oCar, time,best_lap_time) in enumerate(scores): # Wypisujemy miejsce, nazwę auta, czas i najlepszy czas okrążenia
        string = f"Miejsce {i+1}. {car_names[oCar.car_id]} - Czas przejazdu: "+"{0:.3f}".format(time)+", Najszybsze okrążenie: "+"{0:.3f}".format(best_lap_time)
        text = FONT.render(string,True,(242, 245, 47))
        window.blit(text,(WINDOW_WIDTH//2-text.get_width()//2,i*50+100)) 

def update_nick(event,player_nick):
    if 48 <= event.key <= 57:    # Sprawdzamy czy wciśnięto cyfrę
        player_nick += chr(event.key)
    elif pygame.K_a <= event.key <= pygame.K_z and len(player_nick) < 14: # Sprawdzamy czy wciśnięto literę. Limit liter w nicku to 14
        if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]: # Sprawdzamy czy wciśnięto shift
            player_nick += chr(event.key).upper()  # Litera ma być duża
        else: 
            player_nick += chr(event.key) # Litera ma być mała
    elif event.key == pygame.K_BACKSPACE: 
        player_nick = player_nick[:-1] # Usuwamy ostatni znak
    elif event.key == pygame.K_SPACE:
        player_nick += " " # Dodajemy spację
    return player_nick


info = FONT.render("(Spacja - drift, \"K\" - rozlanie oleju)",True,(242, 245, 47))
nick = nick = FONT.render("Wpisz swój nick: "+player_nick,True,(242, 245, 47))
while True: # Pętla główna aplikacji
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Wychodzimy z aplikacji po naciśnięciu X
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Wychodzimy również klawiszem esc
                pygame.quit()
                exit()
            if not scores:
                player_nick = update_nick(event,player_nick)  # Uaktualniamy nick
                nick = FONT.render("Wpisz swój nick: "+player_nick,True,(242, 245, 47))  # Uaktualniamy surface
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Sprawdzamy czy wcisnęliśmy lewy przycisk myszy
                if startButton.isClicked(event.pos) and player_nick and chosen_level: # Sprawdzamy czy myszka najechała na przycisk i czy wpisano nick
                    scores = start_game() # Zaczynamy grę
                    # Następna linijka wykona się dopiero po zakończeniu lub wyjściu z wyścigu
                    chosen_level = 0
                else: # Nie wykrywaj wciśnięcia jeśli właśnie wciskamy start
                    level_buttons_state = [level_buttons[i].isClicked(event.pos) for i in range(3)] # Ustawiamy stan przycisków
                    if True in level_buttons_state and not chosen_level:  # Jeśli jakiś wciśnięty
                        chosen_level = level_buttons_state.index(True)+1 # To ustaw wybrany poziom (1~3)
            
    window.fill((0,0,0)) # Czyścimy ekran
    if scores:
        draw_table(scores) # Rysujemy tabelę wyników
    else:
        window.blit(nick,(WINDOW_WIDTH//2 - nick.get_width()//2,WINDOW_HEIGHT//9*4)) # Wypisujemy nick gracza
    if not scores:
        window.blit(info,(WINDOW_WIDTH//2 - info.get_width()//2,WINDOW_HEIGHT//9*2)) # Wypisujemy informację dla gracza
    if player_nick and chosen_level: # Rysujemy przycisk tylko jeśli podano nick i wybrano poziom
        startButton.draw()
    if not chosen_level:   # Jeśli nie wybrano to rysuj
        level_text = FONT.render("Wybierz poziom:",True,(242, 245, 47))
        window.blit(level_text,(WINDOW_WIDTH//2 - level_text.get_width()//2,WINDOW_HEIGHT//1.6))
        [oButton.draw() for oButton in level_buttons]
    pygame.display.update() # Uaktualniamy ekran