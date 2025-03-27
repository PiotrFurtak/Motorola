import pygame
import random
from ai import *
from Track import *
from Radio import CarRadio  # Zaimportowanie klasy CarRadio
from time import time
pygame.init()

class Game:
    def __init__(self, window):
        self.running = False
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0) # Kolor czarnego tła
        self.YELLOW = (242, 245, 47)
        self.window = window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = window.get_size()
        self.clock = pygame.time.Clock()
        self.pressed_keys = set()
        self.font = pygame.font.SysFont("bahnschrift", 36)  # Czcionka do radia
        self.bigger_font = pygame.font.Font(None,72)
        self.radio = None  # Na początku nie ma radia
        self.buffered = pygame.surface.Surface((8000, 8000))
        turn_img = pygame.image.load("imgs/turn.png")
        forward_img = pygame.image.load("imgs/forward.png")
        self.track = get_level("level-1.txt",self.buffered,turn_img,forward_img)
        self.grass = []
        self.GRASS_IMG = pygame.image.load("imgs/grass.jpg")
        for x in range(0, 8001, self.GRASS_IMG.get_width()):
            for y in range(0, 8001, self.GRASS_IMG.get_height()):
                self.buffered.blit(self.GRASS_IMG,(x,y))
        
        for oTrack in self.track:
            oTrack.scale(6)
        for oTrack in self.track:
            oTrack.draw(4000,4000)

        self.player = Car(self.window,self.track,(-2420,900),pygame.image.load("imgs/red-car.png"),(38,19),90,0)
        ai_amount = 4
        self.enemies = tuple([ai(self.window,self.track,(-2320+100*i,900),pygame.image.load("imgs/red-car.png"),(38,19),90,i+1,self.player) for i in range(ai_amount)])
        self.allCars = tuple([self.player]+list(self.enemies))
        self.max_laps = 3  # Maksymalna liczba okrążeń do zakończenia gry
        self.scores = []
        self.winners = []
        self.begginingTime = time()
        self.oil_img = pygame.image.load("imgs/oil.png")
        self.game_loop()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)

                # Przełączanie radia klawiszem R
                if event.key == pygame.K_r:
                    if self.radio:
                        self.radio.toggle_radio()
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)

        self.player.get_pressed_keys(self.pressed_keys)

    def draw(self):
        # Obliczenie relatywnych pozycji x,y i wycentrowanie
        x = self.WINDOW_WIDTH//2-self.player.x
        y = self.WINDOW_HEIGHT//2-self.player.y

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
            x = self.WINDOW_WIDTH//2-self.enemies[follow_enemy-1].x
            y = self.WINDOW_HEIGHT//2-self.enemies[follow_enemy-1].y

        self.window.blit(self.buffered,(x-4000,y-4000))
        surface = pygame.surface.Surface((self.WINDOW_WIDTH,self.WINDOW_HEIGHT),pygame.SRCALPHA)
        pygame.draw.rect(surface,(0,0,0,200),(0,0,400,250))
        self.player.draw(x,y)
        laps_text = self.font.render(f"Gracz: {self.player.laps}", True, self.WHITE)
        surface.blit(laps_text, (10, 60))
        for oCar in self.enemies:
            oCar.draw(x,y)
            enemy_laps_text = self.font.render(f"Przeciwnik{oCar.car_id}: {oCar.laps}", True, self.WHITE)
            surface.blit(enemy_laps_text, (10, 60+35*oCar.car_id))
        if self.radio:
            text,(x,y),(width,height) = self.radio.draw()
            pygame.draw.rect(surface,(0,0,0,200),(x-10,y-10,width+20,height+20))
            surface.blit(text,(x,y))
        # pygame.draw.circle(surface,(0, 0, 0, 100),(self.WINDOW_WIDTH*7//10+50,self.WINDOW_HEIGHT//2+50),50)
        surface.blit(self.oil_img,(self.WINDOW_WIDTH*7//10,self.WINDOW_HEIGHT//2))
        oil_text = str(self.player.oil_cooldown//60)
        if oil_text == "0": oil_text = "K"
        oil_cooldown = self.bigger_font.render(oil_text,True,self.YELLOW)
        surface.blit(oil_cooldown,(self.WINDOW_WIDTH*7//10+35,self.WINDOW_HEIGHT//2+27))

        player_lap_time = self.font.render("Czas okrążenia: "+"{0:.3f}".format(time()-self.player.laps_times[-1]),True,self.YELLOW)
        surface.blit(player_lap_time,(10,10))
        self.window.blit(surface,(0,0))


            
    def check_winner(self, oCar):
        if oCar.laps >= self.max_laps and oCar not in self.winners:
            self.winners.append(oCar)
            self.scores.append((oCar,time()-self.begginingTime,oCar.best_lap_time))
            if oCar == self.player:
                self.aproximate_scores()
                self.running = False
            else:
                oCar.already_won = True
    
    def aproximate_scores(self):
        all_times = {}
        max_score = self.max_laps*(len(self.track))*1000+130
        for enemy in self.enemies:
            if enemy in self.winners:
                continue
            x,_ = enemy.find_pixel_values(enemy.coords)
            enemy_score = enemy.laps*(len(self.track))*1000+x
            aproximated_time = (time()-self.begginingTime)*max_score/enemy_score
            while aproximated_time in all_times.keys(): aproximated_time += 0.01
            all_times.setdefault(aproximated_time,enemy)
        list = sorted(all_times.keys())
        for key in list:
            self.scores.append((all_times[key],key,all_times[key].best_lap_time))


    def check_collisions(self,oCar:Car):
        for otherCar in self.allCars:
            if oCar == otherCar: continue
            if oCar.isColliding(otherCar):
                oCar.back()

                oCar.Xvelocity, otherCar.Xvelocity = otherCar.velocity*cos(radians(otherCar.angle)), oCar.velocity*cos(radians(oCar.angle))*1.5
                oCar.Yvelocity, otherCar.Yvelocity = otherCar.velocity*sin(radians(otherCar.angle)), oCar.velocity*sin(radians(oCar.angle))*1.5

                oCar.drift, otherCar.drift = 100, 100
        
        if True in [oCar.isColliding(oTrack) for oTrack in self.track]:
            oCar.back()
            oCar.Xvelocity = -oCar.Xvelocity
            oCar.Yvelocity = -oCar.Yvelocity
            oCar.drift = 105

    def game_loop(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.window.fill(self.WHITE)

            self.player.move()
            self.check_collisions(self.player)
            [(enemy.enemy_move(), self.check_collisions(enemy)) for enemy in self.enemies]

            self.player.set_laps()
            [enemy.set_laps() for enemy in self.enemies]
            [self.check_winner(oCar) for oCar in self.allCars]
            [enemy.check_oil_collision(self.player) for enemy in self.enemies]

            num = random.randint(1, 1)
            if self.radio is None:
                self.radio = CarRadio(self.window, self.font, f"music/music{num}.mp3", self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

            self.draw()
            pygame.display.update()
            self.clock.tick(60)
            # print(self.clock.get_fps())            