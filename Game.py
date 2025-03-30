import pygame
import random
from ai import *
from Track import *
from Radio import CarRadio
from time import time,sleep
pygame.init()

class Game:
    def __init__(self, window, player_nick,chosen_level):
        self.PLAYER_NICK = player_nick
        #
        #
        self.CHOSEN_LEVEL = chosen_level # Liczba 1,2 lub 3
        #
        #
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
        start_finish_img = pygame.image.load("imgs/finish.png")
        self.track = get_level(f"level-{self.CHOSEN_LEVEL}.txt",self.buffered,turn_img,forward_img) # Lista kawałków toru
        self.GRASS_IMG = pygame.image.load("imgs/grass.jpg")
        for x in range(0, 8001, self.GRASS_IMG.get_width()):       # Tworzymy w buforze tło zrobione z trawy
            for y in range(0, 8001, self.GRASS_IMG.get_height()):  # składające się z powtarzającej się tekstury
                self.buffered.blit(self.GRASS_IMG,(x,y))
        
        for oTrack in self.track: # Skalujemy tor
            oTrack.scale(6)
        for oTrack in self.track: # Rysujemy tor na buforze
            oTrack.draw(4000,4000)

        self.buffered.blit(pygame.transform.scale_by(start_finish_img,4.7),(-2455+4000,815+4000)) # Rysujemy start/metę

        self.player = Car(self.window,self.track,(-2360,900),pygame.image.load("imgs/green-car.png"),(38,19),90,0)
        ai_amount = 4
        self.enemies = tuple([ai(self.window,self.track,(-2360+91.2*(1+i),900),pygame.image.load("imgs/red-car.png"),(38,19),90,i+1,self.player) for i in range(ai_amount)])
        self.enemies[3].set_position(self.enemies[2].coords) # Ustawiamy pozycję Bota4 na pozycję Bota3
        self.enemies = self.enemies[0:2]+tuple([self.enemies[3]]) # Usuwamy bota 3
        self.allCars = tuple([self.player]+list(self.enemies)) # Krotka z odpowiednio: graczem i 4 botami
        self.max_laps = 3  # Regulacja długości wyścigu
        self.scores = []   # Wyniki czasowe poszczególnych samochodów
        self.winners = []  # Samochody, które już skończyły
        self.begginingTime = time()
        self.oil_img = pygame.image.load("imgs/oil.png")
        self.sorted_cars = []
        self.car_names = {0:self.PLAYER_NICK,1:"Bot1",2:"Bot2",3:"Bot3",4:"Bot4"}
        self.is_countdown_finished = False
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

    def countdown(self):
        surface = pygame.surface.Surface((self.WINDOW_WIDTH,self.WINDOW_HEIGHT),pygame.SRCALPHA) # Półprzeźroczysta powierzchnia
        font = pygame.font.SysFont("bahnschrift", 500)
        three = font.render("3",True,(198, 27, 21))  #
        two = font.render("2",True,(212, 238, 71))   # Odpowiednie napisy
        one = font.render("1",True,(78, 205, 58))    #
        for i,x in enumerate((three,two,one)):
            pygame.draw.rect(surface,(0,0,0,100+50*i),(0,0,self.WINDOW_WIDTH,self.WINDOW_HEIGHT)) # Z każdą sekundą ciemniej
            surface.blit(x,(self.WINDOW_WIDTH//2-x.get_width()//2,self.WINDOW_HEIGHT//2-x.get_height()//2)) # Centrujemy liczbę na powierzchni
            self.window.blit(surface,(0,0)) # Wyrzucamy na ekran
            pygame.display.update() # Uaktualniamy
            sleep(1) # Czekamy sekundę
            self.begginingTime = time()
            self.window.fill(self.WHITE) # Czyścimy ekran
            for oCar in self.allCars: oCar.laps_times[-1] = time()
            self.draw() # Rysujmy wszystko z powrotem

        pygame.display.update() # Uaktualniamy 
        self.is_countdown_finished = True # Zmienna =True powoduje, że nigdy więcej ta funkcja się nie wywoła
        self.begginingTime = time()
        

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
        # if pygame.K_4 in self.pressed_keys:
        #     follow_enemy = 4
            
        if follow_enemy:
            x = self.WINDOW_WIDTH//2-self.enemies[follow_enemy-1].x   # Jeśli wciskamy klawisz 1~4, to kamera
            y = self.WINDOW_HEIGHT//2-self.enemies[follow_enemy-1].y  # podąża za odpowiednim botem
        # 
        # Tutaj jest totalna maskara, bo pisałem to tuż przed deadlinem:
        #
        self.window.blit(self.buffered,(x-4000,y-4000))    # Najpierw wyświetlamy zbuforowane tło wraz z torem
        for oCar in self.allCars: # Rysujemy każde auto
            oCar.draw(x,y)

        text_to_blit = {} # Tu trzymamy napisy wyświetlane w lewym górnym rogu
        for i,oCar in enumerate(self.sorted_cars):
            last_time = "{0:.3f}".format(oCar.laps_times[-1] - self.begginingTime) # string1
            laps = len(oCar.laps_times)-1                                          # string2
            if laps == 0:
                last_time = "0:000"
            lap_text = self.font.render(f"{self.car_names[oCar.car_id]}: {laps}: {last_time}", True, self.WHITE) # Właściwe rysowanie
            text_to_blit.setdefault(lap_text,(10,60+35*i)) # Dodajemy do kolejnki do rysowania

        actual_time = time()-self.player.laps_times[-1]
        player_lap_time = self.font.render("Czas okrążenia: "+"{0:.3f}".format(actual_time if self.is_countdown_finished else 0),True,self.YELLOW)
        text_to_blit.setdefault(player_lap_time,(10,10)) # Info o aktualnym czasie okrążenia gracza

        surface = pygame.surface.Surface((self.WINDOW_WIDTH,self.WINDOW_HEIGHT),pygame.SRCALPHA) # Zmienna surface istnieje po to, żeby rysować
        #                                                                                        # móc rysować półprzeźroczyste obiekty
        all_widths = [oSurface.get_width() for oSurface in list(text_to_blit)[:-1]] # Dodajemy długości napisów z nickami do listy
        all_widths += [360]                                                         # Dodajemy długość napisu z czasem gracza
        width = max(all_widths)                                                     # Szukamy maksimum
        pygame.draw.rect(surface,(0,0,0,200),(0,0,width+15,215)) # Tło na napisy w lewym górnym
        [surface.blit(oSurface,text_to_blit[oSurface]) for oSurface in text_to_blit] # Wyświetlamy napisy

        if self.radio:
            text,(x,y),(width,height) = self.radio.draw()
            pygame.draw.rect(surface,(0,0,0,200),(x-10,y-10,width+20,height+20)) # Rysujemy tekst radia wraz z ciemnym tłem
            surface.blit(text,(x,y))

        surface.blit(self.oil_img,(self.WINDOW_WIDTH*7//10,self.WINDOW_HEIGHT//2)) # Rysujemy ikonkę oleju i cooldown
        oil_text = str(self.player.oil_cooldown//60)
        if oil_text == "0": oil_text = "K"
        oil_cooldown = self.bigger_font.render(oil_text,True,self.YELLOW)
        surface.blit(oil_cooldown,(self.WINDOW_WIDTH*7//10+35,self.WINDOW_HEIGHT//2+27))

        self.window.blit(surface,(0,0)) # Na końcu rysujemy pomocniczą powierzchnię na rzeczywistym ekranie


            
    def check_winner(self, oCar): #Sprawdzamy czy auto skończyło wyścig
        if oCar.laps >= self.max_laps and oCar not in self.winners:
            self.winners.append(oCar)
            self.scores.append((oCar,time()-self.begginingTime,oCar.best_lap_time)) # Dodajemy odpowiednie informacje
            if oCar == self.player:
                self.aproximate_scores() # Jeśli wygrał gracz, to szacujemy czasy przeciwników i wracamy do menu
                self.running = False
                if self.radio:
                    self.radio.toggle_radio()
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

    def sort_cars(self):
        scores = {} # Aktualne wyniki samochodów
        car_list = [0]*(len(self.winners)) # Pusta lista z ewentualnymi miejscami dla aut, które już skończyły
        for oCar in self.allCars:          # Generalnie wygrane auta wkładamy indeksami, a pozostałe metodą `extend`, dlatego tworzę
            if oCar in self.winners:       # z miejscami jedynie dla już wygranych (Reszcie metoda `extend` sama zrobi miejsce na liście)
                car_list[self.winners.index(oCar)] = oCar # Jeśli auto wygrało, to zachowaj miejsce w tabeli
                continue
            x,_ = oCar.find_pixel_values(oCar.coords) # Patrzymy jaki auto ma progres wyścigu
            x += len(self.track) * 1000 * oCar.laps # Uwzględniamy ile ma okrążeń
            while x in scores: x += 1 # Pilnujemy, żeby wynik się nie powtórzył
            scores.setdefault(x,oCar) # Wynik jest kluczem słownika, a auto wartością
        car_list.extend([scores[x] for x in sorted(scores)[::-1]]) # Sortujemy po wynikach malejąco i dodajemy odpowiednie samochody do listy
        return car_list

    def game_loop(self):
        self.running = True
        while self.running:
            self.handle_events() # Sprawdzamy eventy
            self.window.fill(self.WHITE) # Czyścimy ekran

            self.player.move() # Przesuwamy gracza
            self.check_collisions(self.player) # Sprawdzamy kolizje
            [(enemy.enemy_move(), self.check_collisions(enemy)) for enemy in self.enemies] # To samo z botami
            self.car_progress = [oCar.find_pixel_values(oCar.coords)[0] for oCar in self.allCars]


            self.player.set_laps() # Aktualizujemy liczbę okrążeń gracza
            [enemy.set_laps() for enemy in self.enemies] # -||- botów
            [self.check_winner(oCar) for oCar in self.allCars] # Sprawdzamy, czy auto skończyło wyścig
            [enemy.check_oil_collision(self.player) for enemy in self.enemies] # Sprawdzamy czy przeciwnicy nie wjechali w olej
            self.sorted_cars = self.sort_cars() # Ustawiamy auta od najlepszego do najgorszego

            num = random.randint(1, 2) # Wybieramy piosenkę
            if self.radio is None:
                self.radio = CarRadio(self.window, self.font, f"music/music{num}.mp3", self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

            self.draw() # Rysujemy wszystko co mamy narysować
            pygame.display.update() # Aktualizacja na ekranie
            if not self.is_countdown_finished: self.countdown() # Wywołaj funkcję tylko jeśli jej nie wywoływaliśmy wcześniej
            self.clock.tick(60) # Ustawiamy FPS na 60          