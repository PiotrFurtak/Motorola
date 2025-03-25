import pygame
import sys
import random
from Car import *
from Track import *
from Radio import CarRadio  # Zaimportowanie klasy CarRadio
from ai import ai

pygame.init()


class Game(ai):
    def __init__(self, window):
        self.running = False
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)  # Kolor czarnego tła
        self.window = window
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = window.get_size()
        self.clock = pygame.time.Clock()
        self.pressed_keys = set()
        self.font = pygame.font.Font(None, 36)  # Czcionka do wyświetlania tekstu
        self.radio = None  # Na początku nie ma radia
        self.lap_count = 0  # Licznik okrążeń gracza
        self.enemy_lap_count = 0  # Licznik okrążeń przeciwnika
        self.max_laps = 5  # Maksymalna liczba okrążeń do zakończenia gry
        self.winner = None  # Przechowywanie zwycięzcy
        self.end_timer = 0  # Timer do stopniowego kończenia gry
        self.nazwa = [""]

        turn_img = pygame.image.load("imgs/turn.png")
        forward_img = pygame.image.load("imgs/forward.png")
        self.track = get_level("level-1.txt", window, turn_img, forward_img)
        for oTrack in self.track:
            oTrack.scale(3)

        self.grass = []
        self.GRASS_IMG = pygame.image.load("imgs/grass.jpg")
        for x in range(-2000, 2001, self.GRASS_IMG.get_width()):
            for y in range(-2000, 2001, self.GRASS_IMG.get_height()):
                self.grass.append(Sprite(self.window, (x, y), self.GRASS_IMG, (0, 0)))

        self.player = Car(self.window, self.track, (0, -500), pygame.image.load("imgs/red-car.png"), (38, 19),
                          is_player=True)
        self.enemy = Car(self.window, self.track, (0, -400), pygame.image.load("imgs/red-car.png"), (38, 19))
        self.point = Sprite(self.window, (0, 0), pygame.image.load("imgs/point.png"), (2, 2), 0)

        self.game_loop()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)
                if event.key == pygame.K_r:  # Przełączanie radia klawiszem R
                    if self.radio:
                        self.radio.toggle_radio()
            elif event.type == pygame.KEYUP:
                self.pressed_keys.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                values = self.find_pixel_values(self.get_real_point(event.pos))
                if values is not None:
                    print(values)

        self.player.get_pressed_keys(self.pressed_keys)

    def draw(self):
        # Jeśli gra zakończona, rysujemy czarne tło z komunikatem o zwycięzcy
        if self.winner:
            self.window.fill(self.BLACK)
            winner_text = self.font.render(f"{self.winner} wygrał!", True, (255, 0, 0))
            self.window.blit(winner_text, (self.WINDOW_WIDTH // 2 - 100, self.WINDOW_HEIGHT // 2))
            pygame.display.update()
            return

        # Normalne rysowanie, jeśli gra nie jest zakończona
        x = self.WINDOW_WIDTH // 2 - self.player.x
        y = self.WINDOW_HEIGHT // 2 - self.player.y
        if pygame.K_1 in self.pressed_keys:
            x = self.WINDOW_WIDTH // 2 - self.enemy.x
            y = self.WINDOW_HEIGHT // 2 - self.enemy.y

        for oSprite in self.grass:
            oSprite.draw(x, y)
        for oSprite in self.track:
            oSprite.draw(x, y)
        self.enemy.draw(x, y)
        self.player.draw(x, y)
        self.point.draw(x, y)

        # Wyświetlenie liczby okrążeń
        laps_text = self.font.render(f"Okrążenia gracza: {self.lap_count}", True, (0, 0, 0))
        self.window.blit(laps_text, (10, 10))
        enemy_laps_text = self.font.render(f"Okrążenia przeciwnika: {self.enemy_lap_count}", True, (0, 0, 0))
        self.window.blit(enemy_laps_text, (10, 40))

        if self.radio:
            self.radio.draw()

    def check_winner(self, nazwa):
        # Sprawdzamy, czy gracz ukończył wyścig
        if self.lap_count >= self.max_laps and self.enemy_lap_count >= self.max_laps:
            self.winner = nazwa[-1]
            self.end_timer = 300  # Ustawiamy timer na 3 sekundy

    def game_loop(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.window.fill(self.WHITE)

            if self.winner:
                self.end_timer -= 1
                if self.end_timer <= 0:
                    self.running = False
            else:
                # Zatrzymanie gracza po ukończeniu 5 okrążeń
                if self.lap_count >= self.max_laps:
                    self.player.velocity = 0
                    self.player.Xvelocity = 0
                    self.player.Yvelocity = 0
                    self.player.acceleration = 0
                    self.player.Xacceleration = 0
                    self.player.Yacceleration = 0
                    self.nazwa.append("Gracz")

                # Zatrzymanie przeciwnika po ukończeniu 5 okrążeń
                if self.enemy_lap_count >= self.max_laps:
                    self.enemy.velocity = 0
                    self.enemy.Xvelocity = 0
                    self.enemy.Yvelocity = 0
                    self.enemy.acceleration = 0
                    self.enemy.Xacceleration = 0
                    self.enemy.Yacceleration = 0
                    self.nazwa.append("Bot1")

                self.player.move()  # Gracz nie porusza się, jeśli jego prędkość jest 0
                self.enemy_move()  # Bot nadal porusza się, jeśli jego prędkość nie jest 0
                self.player.set_loops()
                self.enemy.set_loops()
                self.lap_count = self.player.loops  # Aktualizacja licznika okrążeń gracza
                self.enemy_lap_count = self.enemy.loops  # Aktualizacja licznika okrążeń przeciwnika
                self.check_winner(self.nazwa)

            num = random.randint(1, 1)
            if self.radio is None:
                self.radio = CarRadio(self.window, self.font, f"music/music{num}.mp3", self.WINDOW_WIDTH,
                                      self.WINDOW_HEIGHT)

            self.draw()
            pygame.display.update()
            self.clock.tick(60)

