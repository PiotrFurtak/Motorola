Sprite.py zawiera funkcje niczym w Scratchu odpowiadające za m.in. poruszanie i sprawdzanie kolizji obiektów. Docelowo każda rzecz na ekranie będzie obiektem tej klasy lub jej dzieckiem.
Car.py zawiera funkcje odpowiadające za ruch samochodu. Jest dzieckiem klasy Sprite.
Game.py jest jakby "instancją gry". Tworzy wszystkie obiekty i uruchamia pętlę główną.
Main.py docelowo ma zawierać cały interfejs, dźwięki, wybór poziomu i po naciśnięciu odpowiedniego przycisku na ekranie będzie tworzyć instancję gry i uruchamiać pętlę główną.
Po zakończeniu poziomu lub wyjściu z rozgrywki, powinien być powrót do interfejsu (Menu głównego), gdzie można np. wybrać inny poziom i ponownie zacząć grę. 
