from Sprite import Sprite
from math import cos,sin,radians,copysign
from time import time
import pygame

class Car(Sprite):
    def __init__(self,window,track,coords,image,centre_point,angle,car_id):
        self.car_id = car_id
        Sprite.__init__(self,window,coords,image,centre_point,angle,is_player=car_id==0)
        self.track = track
        self.stear = 0
        self.joystick_x = 0 # czy auto ma jechać lewo-prawo (-1=lewo, 1=prawo)
        self.joystick_y = 0 # czy auto ma jechać przód-tył (1=przód, -1=tył)
        self.last_pos = (0,0,0)
        self.is_braking = False  # Czy samochód hamuje
        self.pressed_keys = set() # Informacja o klawiszach
        self.acceleration = 0 # Przyspieszenie liniowe
        self.Xacceleration = 0 # Przyspieszenie w kierunku X, można to interpretować jako składową poziomą siły bezwładności
        self.Yacceleration = 0 # Analogicznie w kierunku Y. To będzie wykorzystane przy driftowaniu
        self.velocity = 0 # Prędkość liniowa
        self.Xvelocity = 0 # Bezwładna prędkość w kierunku X
        self.Yvelocity = 0 # Bezwładna prędkość w kierunku Y
        self.drift = 0 # drift przyjmuje wartości 0~100, gdzie 0 oznacza, że przy poruszaniu bierzemy pod uwagę tylko prędkość liniową,
        # 100 oznacza, że bierzemy pod uwagę tylko prędkości od bezwładności (ślizganie się niczym na lodzie),
        # a wartość np. 20 oznacza coś pomiędzy, czyli lekki drift
        self.tile_id = 0 # id pola, na którym się auto znajduje
        self.laps = 0 # licznik okrążeń
        self.laps_times = [time()] # czasy wykonania okrążeń
        self.best_lap_time = 1000000 # najlepszy czas (duża liczba, żeby cokolwiek ją mogło przebić)
        self.oil_cooldown = 0 # cooldown rozlania oleju
        self.oil_coords = (0,0) # koordynaty rozlania
        self.oil_radius = 0 # promień plamy
        self.oiled_time = 0 # ile klatek auto będzie się jeszcze ślizgać (odnawia się po dotknięciu oleju)
        self.hitbox = Sprite(self.window,coords,pygame.image.load("imgs/car-hitbox.png"),centre_point)
        self.hitbox.scale_by(1/6) # Skalujemy, żeby zyskać na wydajności

    def draw(self,x,y):
        if self.oil_cooldown == 0 and self.oil_radius > 0: # Plama się po pewnym czasie zmniejsza
            self.oil_radius -= 1
        if self.oil_radius > 0: # Rysujemy plamę oleju jeśli trzeba
            pygame.draw.circle(self.window,(0,0,0),(x+self.oil_coords[0],y+self.oil_coords[1]),self.oil_radius)
            if self.oil_radius < 75 and self.oil_cooldown > 0: # Plama się początkowo zwiększa
                self.oil_radius += 1
        Sprite.draw(self,x,y) # Rysujemy auto

    def get_pressed_keys(self, pressed_keys):
        self.joystick_y = 0 # 
        self.joystick_x = 0 # Resetujemy wszystko
        self.is_braking = False  #

        self.pressed_keys = pressed_keys # Bierzemy informację o klawiszach

        # Ruch do przodu i do tyłu
        if pygame.K_UP in self.pressed_keys or pygame.K_w in self.pressed_keys:
            self.joystick_y += 1
        if pygame.K_DOWN in self.pressed_keys or pygame.K_s in self.pressed_keys:
            self.joystick_y -= 1

        # Skręt
        if pygame.K_LEFT in self.pressed_keys or pygame.K_a in self.pressed_keys:
            self.joystick_x += 1
        if pygame.K_RIGHT in self.pressed_keys or pygame.K_d in self.pressed_keys:
            self.joystick_x -= 1

        # Hamowanie
        if pygame.K_SPACE in self.pressed_keys:
            self.is_braking = True

        # Rozlewanie oleju i cooldown
        if self.oil_cooldown > 0:
            self.oil_cooldown += -1
        if pygame.K_k in self.pressed_keys:
            self.spill_oil()

    def spill_oil(self): # Rozlewamy olej i ustawiamy ile czasu ma być aktywny (Wywołuje tą funkcję tylko gracz)
        if self.oil_cooldown > 0:
            return
        self.oil_coords = self.x,self.y
        self.oil_radius = 1
        self.oil_cooldown = 60*15

    def check_oil_collision(self,player): # Sprawdzamy czy auto wpadło w plamę oleju
        if player.oil_radius == 0:
            return False
        oil = pygame.surface.Surface((player.oil_radius*2,player.oil_radius*2))
        mask = pygame.mask.from_surface(oil)
        if self.mask.overlap(mask,(self.x-player.oil_coords[0],self.y-player.oil_coords[1])): # Patrzymy czy dotyka
            self.oiled_time = 60*3 # Jak tak, to przez 3 sekundy miej debuff
            return True
        return False
    
    def isColliding(self,oSprite): # Sprawdzamy kolizje samochodów z innymi duszkami
        x,y = self.coords
        self.hitbox.set_position((x/6,y/6))
        self.hitbox.set_angle(self.angle)
        return Sprite.isColliding(self.hitbox,oSprite.hitbox) # De facto sprwadzamy kolizje hitboxów tych duszków

    def turn(self): # Aktualizujemy kąt skrętu. Dzięki tej funkcji skręt płynnie rośnie i płynnie się wygasza
        if self.joystick_x == 0:
            self.stear *= 0.3
        self.stear += 4 * self.joystick_x
        if self.is_braking:
            self.stear *= 0.9
            return
        self.stear *= 0.85

    def move(self): # Funkcja inicjująca cały ruch, aktualizująca przyspieszenia, prędkości itp.
        if self.oiled_time > 0: # Debuff jeśli auto dotknęło oleju
            self.oiled_time += -1
            self.drift = 95
            self.Xacceleration = 0
            self.Yacceleration = 0
        self.last_pos = (self.x,self.y,self.angle) # W razie kolizji z autem/torem można cofnąć do poprzedniej pozycji

        self.acceleration += 0.7*self.joystick_y                           #
        self.Xacceleration += 0.7*self.joystick_y*cos(radians(self.angle)) # Zwiększamy przyspieszenia
        self.Yacceleration += 0.7*self.joystick_y*sin(radians(self.angle)) #

        if self.is_player:
            self.turn()

        self.rotate(self.stear/200*self.velocity) # Obrót zależy od prędkości liniowej i skrętu
        if self.joystick_x and abs(self.velocity) > 10: # Przy większej prędkości drift automatycznie rośnie
            self.drift += 1

        if self.is_braking: # Na ręcznym jeździ się wolniej (teorytycznie powinno się hamować do zera, ale kij z tym)
            self.drift += 3 # Zwieksza to diametralnie drift
            if not self.joystick_x:
                self.velocity *= 0.9
        
        self.drift *= 0.96        #
        self.acceleration *= 0.5  # Wszzystko się naturalnie wygasza
        self.Xacceleration *= 0.5 #
        self.Yacceleration *= 0.5 #

        self.velocity += self.acceleration   #
        self.Xvelocity += self.Xacceleration # Na logikę tak działa fizyka...
        self.Yvelocity += self.Yacceleration #

        self.velocity *= 0.96
        if not self.oiled_time:    # Wygaszanie różni się, jeśli auto ma debuffa
            self.Xvelocity *= 0.96
            self.Yvelocity *= 0.96
        else:
            self.Xvelocity *= 0.98
            self.Yvelocity *= 0.98

        self.not_drift = 100 - self.drift # I tu się dzieje magia
        distance = self.velocity*self.not_drift/100/1 # Bierzemy tyle procent normalnej prędkości ile nie driftujemy
        dx = self.Xvelocity*self.drift/100/1.5  # Bierzemy tyle bezwładności ile jest driftu
        dy = -self.Yvelocity*self.drift/100/1.5 # (Dzielenie przez 1.5 jest tylko dlatego, że losowo wydaje się wyglądać lepiej)
        self.forward(distance)      #
        self.change_position(dx,dy) # Tak działa fizyka 
        amount = len(self.track)
        possible_id = ((self.tile_id-1)%amount, self.tile_id, (self.tile_id+1)%amount) # Patrzymy na sąsiednie pola toru
        if True in [self.isColliding(self.track[id-1]) for id in possible_id]: # Sprawdzamy kolizje
            self.back()              # 
            self.Xvelocity = -dx*1.5 # Cofamy i odbijamy samochód
            self.Yvelocity = -dy*1.5 #
            self.drift = 100         # Ustawiamy też ślizg na maksa (Niestety nie działa tak jakbym chciał :(      )

    def back(self):
        self.set_position(self.last_pos[0:2]) # Cofamy do zapisanej pozycji
        self.set_angle(self.last_pos[2])
    
    def is_next_lap(self,oTrack): # Sprawdzamy czy dane pole jest następnym okrążeniem już
        if oTrack == None:
            return 0
        new_tile_id = oTrack.id
        if new_tile_id < 3 and self.tile_id > 10:
            if self.laps != len(self.laps_times)-1:
                return 1
            self.laps_times.append(time())
            if self.laps_times[-1] - self.laps_times[-2] < self.best_lap_time:
                self.best_lap_time = self.laps_times[-1] - self.laps_times[-2]
            return 1
        elif self.tile_id < 3 and new_tile_id > 10:
            return -1
        return 0
    
    def set_laps(self): # Aktualizujemy licznik pętli
        oTrack = self.find_tile(self.coords)
        if oTrack == None:
            return
        new_tile_id = oTrack.id
        self.laps += self.is_next_lap(oTrack)
        self.tile_id = new_tile_id

    def find_tile(self,coords): # Szukamy jakie jest id pola toru, do którego należy punkt o współrzędnych x,y
        for oTrack in self.track:
            x,y = coords
            if oTrack.x-oTrack.centre_point[0] <= x <= oTrack.x+oTrack.centre_point[0] and oTrack.y-oTrack.centre_point[1] <= y <= oTrack.y+oTrack.centre_point[1]:
                return oTrack
        return None
    
    def find_pixel_values(self,coords): # Dla danego piksela w grze, zwróć wartości x,y "Zakrzywionej geometrii"
        oTrack:Sprite = self.find_tile(coords)
        if oTrack:
            values = oTrack.get_pixel_values(coords)
            return values[0]+1000*oTrack.id,values[1]
        return None