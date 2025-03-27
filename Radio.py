import pygame

music_dict = {
        "music/music1.mp3": "Love Will Save The World" # Tytuł i lokalizacja pliku z utworem
    }


class CarRadio:

    def __init__(self, screen, font, music_file, width, height):
        self.screen = screen
        self.font = font
        self.music_file = music_file
        self.radio_on = False
        self.width = width
        self.height = height
        pygame.mixer.init()

    def toggle_radio(self): # Przełączamy radio (on/off)
        if self.radio_on:
            pygame.mixer.music.stop()
            self.radio_on = False
        else:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1)  # Odtwarzanie w pętli
            self.radio_on = True

    def draw(self): # Zwraca parametry potrzebne do narysowania tekstu
        status_text = f"Radio (R): {music_dict[self.music_file]}" if self.radio_on else "Radio (R): WYŁĄCZONE"
        text:pygame.Surface = self.font.render(status_text, True, (242, 245, 47))
        return text,(self.width // 1.7 - text.get_width() // 3, self.height // 1.07),text.get_size()

