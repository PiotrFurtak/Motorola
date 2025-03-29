import pygame
import random
from ai import *
from Track import *
from Radio import CarRadio
from time import time
pygame.init()

class Game:
    def __init__(self, window, player_nick):
        self.PLAYER_NICK = player_nick
        self.running = False
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.YELLOW = (242, 245, 47)
        self.window = window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = window.get_size()
        self.clock = pygame.time.Clock()
        self.pressed_keys = set()
        self.font = pygame.font.SysFont("bahnschrift", 36)
        self.bigger_font = pygame.font.Font(None,72)
        self.radio = None
        self.buffered = pygame.surface.Surface((8000, 8000)) # Tu będzie zbuforowany tor, w celu poprawy wydajności
        turn_img = pygame.image.load("imgs/turn.png")
        forward_img = pygame.image.load("imgs/forward.png")
        self.track = get_level("level-1.txt",self.buffered,turn_img,forward_img) # Lista kawałków toru
        self.GRASS_IMG = pygame.image.load("imgs/grass.jpg")
        for x in range(0, 8001, self.GRASS_IMG.get_width()):       # Tworzymy w buforze tło zrobione z trawy
            for y in range(0, 8001, self.GRASS_IMG.get_height()):  # składające się z powtarzającej się tekstury
                self.buffered.blit(self.GRASS_IMG,(x,y))
        
        for oTrack in self.track: # Skalujemy tor
            oTrack.scale(6)
        for oTrack in self.track: # Rysujemy tor na buforze
            oTrack.draw(4000,4000)

        self.player = Car(self.window,self.track,(-2420,900),pygame.image.load("imgs/red-car.png"),(38,19),90,0)
        ai_amount = 4
        self.enemies = tuple([ai(self.window,self.track,(-2320+100*i,900),pygame.image.load("imgs/red-car.png"),(38,19),90,i+1,self.player) for i in range(ai_amount)])
        self.allCars = tuple([self.player]+list(self.enemies)) # Krotka z odpowiednio: graczem i 4 botami
        self.max_laps = 3  # Regulacja długości wyścigu
        self.scores = []   # Wyniki czasowe poszczególnych samochodów
        self.winners = []  # Samochody, które już skończyły
        self.begginingTime = time()
        self.oil_img = pygame.image.load("imgs/oil.png")
        self.game_loop()  # Zaczynamy grę


    def handle_events(self):
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: # Po kliknięciu w X wracamy do menu
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key) # Zbieramy informacje o klikniętych klawiszach
                
                if event.key == pygame.K_r: # Przełączanie radia klawiszem R
                    if self.radio:
                        self.radio.toggle_radio()
                if event.key == pygame.K_ESCAPE: # Po naciśnięciu klawisza esc wracamy do menu
                    self.running = False

            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)

        self.player.get_pressed_keys(self.pressed_keys) # Wysyłamy autu gracza informację o klawiszach

    def draw(self): # Funkcja rysująca wszystko na ekranie
        x = self.WINDOW_WIDTH//2-self.player.x # Relatywne pozycje x i y potrzebne, żeby
        y = self.WINDOW_HEIGHT//2-self.player.y # kamera podążała za autem gracza

        follow_enemy = 0
        if pygame.K_1 in self.pressed_keys:
            follow_enemy = 1
        if pygame.K_2 in self.pressed_keys:
            follow_enemy = 2
        if pygame.K_3 in self.pressed_keys:
            follow_enemy = 3
        if pygame.K_4 in self.pressed_keys:
            follow_enemy = 4
            
        if follow_enemy:
            x = self.WINDOW_WIDTH//2-self.enemies[follow_enemy-1].x   # Jeśli wciskamy klawisz 1~4, to kamera
            y = self.WINDOW_HEIGHT//2-self.enemies[follow_enemy-1].y  # podąża za odpowiednim botem
        # 
        # Tutaj jest totalna maskara, bo pisałem to tuż przed deadlinem:
        #
        self.window.blit(self.buffered,(x-4000,y-4000))    # Najpierw wyświetlamy zbuforowane tło wraz z torem
        surface = pygame.surface.Surface((self.WINDOW_WIDTH,self.WINDOW_HEIGHT),pygame.SRCALPHA) # Zmienna surface istnieje po to, żeby
        pygame.draw.rect(surface,(0,0,0,200),(0,0,400,250)) # Tło na napisy w lewym górnym       # Móc rysować półprzeźroczyste obiekty
        self.player.draw(x,y) # Rysujemy auto gracza

        laps_text = self.font.render(f"{self.PLAYER_NICK} : {len(self.player.laps_times)-1}", True, self.WHITE) # Rysujemy info o okrążeniach gracza
        surface.blit(laps_text, (10, 60))

        for oCar in self.enemies: # Rysujemy każdego przeciwnika wraz z info o jego okrążeniach
            oCar.draw(x,y)

            enemy_laps_text = self.font.render(f"Przeciwnik{oCar.car_id}: {oCar.laps}", True, self.WHITE)
            surface.blit(enemy_laps_text, (10, 60+35*oCar.car_id))

        if self.radio:
            text,(x,y),(width,height) = self.radio.draw()
            pygame.draw.rect(surface,(0,0,0,200),(x-10,y-10,width+20,height+20)) # Rysujemy tekst radia wraz z ciemnym tłem
            surface.blit(text,(x,y))

        surface.blit(self.oil_img,(self.WINDOW_WIDTH*7//10,self.WINDOW_HEIGHT//2)) # Rysujemy ikonkę oleju i cooldown
        oil_text = str(self.player.oil_cooldown//60)
        if oil_text == "0": oil_text = "K"
        oil_cooldown = self.bigger_font.render(oil_text,True,self.YELLOW)
        surface.blit(oil_cooldown,(self.WINDOW_WIDTH*7//10+35,self.WINDOW_HEIGHT//2+27))

        player_lap_time = self.font.render("Czas okrążenia: "+"{0:.3f}".format(time()-self.player.laps_times[-1]),True,self.YELLOW)
        surface.blit(player_lap_time,(10,10))  # Rysujemy info o czasie aktualnego okrążenia
        
        self.window.blit(surface,(0,0)) # Na końcu rysujemy pomocniczą powierzchnię na rzeczywistym ekranie


            
    def check_winner(self, oCar): #Sprawdzamy czy auto skończyło wyścig
        if oCar.laps >= self.max_laps and oCar not in self.winners:
            self.winners.append(oCar)
            self.scores.append((oCar,time()-self.begginingTime,oCar.best_lap_time)) # Dodajemy odpowiednie informacje
            if oCar == self.player:
                self.aproximate_scores() # Jeśli wygrał gracz, to szacujemy czasy przeciwników i wracamy do menu
                self.running = False
            else:
                oCar.already_won = True # Dajemy znać przeciwnikom, że już skończyli
    
    def aproximate_scores(self):
        all_times = {}
        max_score = self.max_laps*(len(self.track))*1000+130 # Patrzymy na maksymalny możliwy wynik
        for enemy in self.enemies:
            if enemy in self.winners:
                continue
            x,_ = enemy.find_pixel_values(enemy.coords)
            enemy_score = enemy.laps*(len(self.track))*1000+x  # Liczymy wynik bota
            aproximated_time = (time()-self.begginingTime)*max_score/enemy_score # Liczymy proporcjonalnie czas
            while aproximated_time in all_times.keys(): aproximated_time += 0.01 # Będziemy sortować po czasach, więc są one kluczami w słownikach
            all_times.setdefault(aproximated_time,enemy)                         # Dlatego dodajemy 0.01, żeby klucz się nie powtórzył
        list = sorted(all_times.keys())
        for key in list:
            self.scores.append((all_times[key],key,all_times[key].best_lap_time)) # Dodajemy do listy wyników w posortowanej kolejności


    def check_collisions(self,oCar:Car):
        for otherCar in self.allCars:       # Sprawdzamy kolizje z wszystkimi innymi samochodami
            if oCar == otherCar: continue
            if oCar.isColliding(otherCar):
                oCar.back()                 # Cofamy samochód
                # Zamieniamy samochody prędkościami, żeby uzyskać efekt odbicia
                oCar.Xvelocity, otherCar.Xvelocity = otherCar.velocity*cos(radians(otherCar.angle)), oCar.velocity*cos(radians(oCar.angle))*1.5
                oCar.Yvelocity, otherCar.Yvelocity = otherCar.velocity*sin(radians(otherCar.angle)), oCar.velocity*sin(radians(oCar.angle))*1.5

                oCar.drift, otherCar.drift = 100, 100 # drift=100 tworzy efekt ślizgu

    def game_loop(self):
        self.running = True
        while self.running:
            self.handle_events() # Sprawdzamy eventy
            self.window.fill(self.WHITE) # Czyścimy ekran

            self.player.move() # Przesuwamy gracza
            self.check_collisions(self.player) # Sprawdzamy kolizje
            [(enemy.enemy_move(), self.check_collisions(enemy)) for enemy in self.enemies] # To samo z botami

            self.player.set_laps() # Aktualizujemy liczbę okrążeń gracza
            [enemy.set_laps() for enemy in self.enemies] # -||- botów
            [self.check_winner(oCar) for oCar in self.allCars] # Sprawdzamy, czy auto skończyło wyścig
            [enemy.check_oil_collision(self.player) for enemy in self.enemies] # Sprawdzamy czy przeciwnicy nie wjechali w olej

            num = random.randint(1, 1) # Wybieramy piosenkę (Ale jest tylko jedna)
            if self.radio is None:
                self.radio = CarRadio(self.window, self.font, f"music/music{num}.mp3", self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

            self.draw() # Rysujemy wszystko co mamy narysować
            pygame.display.update() # Aktualizacja na ekranie
            self.clock.tick(60) # Ustawiamy FPS na 60          