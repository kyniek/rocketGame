

## Prompt dla LLM (Python + Arcade)

Jesteś asystentem programistycznym. Masz za zadanie zaimplementować **Proof of Concept (POC)** edukacyjnej gry w języku **Python 3.10+** z wykorzystaniem biblioteki **Arcade** (https://api.arcade.academy/). Gra działa w oknie, obsługuje klawiaturę, rysuje siatkę, zarządza stanami. **Każda klasa i kluczowa funkcja musi być pokryta testami jednostkowymi** (pytest). Dodatkowo napisz przynajmniej jeden test integracyjny dla głównego przepływu gry (np. symulacja ruchów i kolizji).

### Specyfikacja gry (tożsama z wcześniejszą, ale dostosowana do Arcade)

Gra toczy się na siatce o wymiarach **30 kolumn (oś X) × 3 wiersze (oś Y)**. Gracz steruje rakietą za pomocą klawiszy strzałek:

- **Strzałka w górę/dół** – przesunięcie w tym samym wierszu (kolumna pozostaje ta sama), blokada na brzegi (nie wychodzi poza 0–2).
- **Strzałka w prawo** – ruch do przodu (zwiększenie kolumny o 1, wiersz ten sam). **Przed wykonaniem ruchu** sprawdzana jest kolizja z przeszkodą w docelowej komórce. Jeśli kolizja – gracz traci 1 życie, a rakieta wraca do pozycji startowej (kolumna 0, losowy wiersz wybrany na początku gry). Jeśli nie ma kolizji – ruch jest wykonywany, a **po udanym ruchu** z prawdopodobieństwem 20% uruchamiany jest challenge (pytanie).

#### Plansza i generowanie labiryntu

- **Kolumna 0 (start)** – brak przeszkód. Pozycja startowa rakiety to losowy wiersz (0-2).
- **Kolumna 29 (meta)** – brak przeszkód. Meta znajduje się w losowym wierszu (może być takim samym jak start). Po wejściu rakiety na dokładnie to pole – gra zostaje zakończona zwycięstwem i wyświetlany jest ekran końcowy z wynikami.
- **Kolumny 1–28** – każda może zawierać **maksymalnie jedną przeszkodę**. Generator labiryntu (`MazeGenerator`) działa:
  1. Losuje **ścieżkę** – dla każdej kolumny 0–29 wybiera jeden wolny wiersz (ścieżka może być dowolna, ale musi istnieć ciągły przejazd? W tym wypadku wystarczy, że w każdej kolumnie jest co najmniej jeden wolny wiersz, a przeszkody są w innych wierszach). W kolumnie startowej ścieżka to wiersz startowy, w kolumnie mety – wiersz mety.
  2. Dla **50% kolumn spoza ścieżki** (z wyłączeniem kolumny startowej i mety) losowo wybiera jeden wiersz **różny od ścieżki** i umieszcza tam przeszkodę.
- Wynik generatora: lista list `grid[30][3]` z wartościami `'empty'`, `'obstacle'`, `'start'`, `'goal'`.

#### Fog of war (mgła wojny)

Gracz widzi:
- całą swoją aktualną kolumnę,
- wszystkie kolumny, które już odwiedził (od 0 do bieżącej kolumny),
- **jedną kolumnę do przodu** (bieżąca kolumna + 1).
Reszta planszy jest zasłonięta (nie rysowana lub rysowana jako czarne pola). Po stracie życia i powrocie do startu – odkryta część planszy resetuje się do widoczności tylko kolumny 0 i 1. `FogOfWar` przechowuje macierz `discovered` 30×3 (bool) i aktualizuje się przy każdym ruchu lub resecie.

#### Challenge (zagadki)

- Wczytywane z pliku `questions.json` (przykładowa struktura poniżej).
- Dwa typy:
  - **Wielokrotnego wyboru (A/B/C)** – gdy w JSON istnieją pola `answerB` i `answerC` (niepuste).
  - **Tekstowy** – gdy `answerB` i `answerC` są puste (gracz wpisuje odpowiedź w polu tekstowym).
- Obsługa w Arcade: pojawia się modal (nowy widok lub nakładka) blokujący sterowanie rakietą. Gracz wybiera odpowiedź (klawisze 1,2,3 lub kliknięcie, lub wpisuje tekst i klika przycisk „OK” / wciska `Enter`). Brak limitu czasu. Po udzieleniu odpowiedzi:
  - Jeśli poprawna → dodaj 1 punkt.
  - Jeśli błędna → odejmij 1 życie (z 3 dostępnych).
- Historia błędnych odpowiedzi (treść pytania, odpowiedź gracza, poprawna odpowiedź) jest przechowywana i wyświetlana na ekranie końcowym.

#### System żyć i punktów

- Start: 3 życia, 0 punktów.
- Wizualizacja: w prawym górnym rogu zielona liczba żyć (`LivesManager`) i biała liczba punktów (`ScoreManager`). Klasy te mają być odseparowane od UI (emitują zdarzenia lub są obserwowane przez widok).
- Po utracie wszystkich żyć – gra kończy się porażką i wraca do ekranu startowego (reset wszystkich stanów).

#### Kolizje i priorytety (powtórzenie)

1. Ruch w prawo: jeśli następna komórka to `obstacle` → natychmiast utrata życia i respawn (bez challenge).
2. Jeśli następna komórka to `goal` → zwycięstwo.
3. Jeśli jest pusta → wykonaj ruch, **potem** z 20% szansą na challenge.

#### Renderowanie (Arcade)

- Siatka: czarne tło, zielone linie (można użyć `arcade.draw_rectangle` lub `draw_grid`).
- Każda komórka ma rozmiar np. 40×40 pikseli.
- Rysowanie obiektów:
  - **Rakieta** – niebieski kwadrat z białym trójkątem (lub po prostu kolorowy kwadrat).
  - **Przeszkoda** – czerwony kwadrat.
  - **Meta** – żółty kwadrat (może z napisem "META").
  - **Start** – zielony kwadrat (ale start jest tylko pozycją początkową rakiety, nie rysuje się jako osobny obiekt? Lepiej narysować pole startowe jako jasnozielone).

Na razie bez obrazków PNG – każdy obiekt rysujemy jako kolorowy kształt. Jednak w kodzie zachowaj strukturę, która w przyszłości pozwoli dodać sprite (np. zmieniając metodę `draw` na rysowanie tekstury).

### Wymagania architektoniczne (klasy Python/Arcade)

Zaimplementuj następujące klasy i moduły. Stosuj typowanie (`typing`). Użyj wzorców: obserwator dla UI, kompozycja.

#### 1. `models/maze_generator.py`
- Klasa `MazeGenerator` z metodą statyczną lub instancyjną `generate(start_row: int, goal_row: int) -> list[list[str]]` zwracającą siatkę 30×3 (wartości: `'empty'`, `'obstacle'`, `'start'`, `'goal'`). W kolumnie 0 ustaw `'start'` w wierszu `start_row`, w kolumnie 29 `'goal'` w wierszu `goal_row`.

#### 2. `models/game_grid.py`
- Klasa `GameGrid` – przechowuje siatkę. Metody: `get_cell(col, row)`, `set_cell(col, row, value)`, `is_walkable(col, row)` (True jeśli nie przeszkoda i w granicach).

#### 3. `models/rocket.py`
- Klasa `Rocket` – atrybuty `col` (int), `row` (int). Metody: `move_up()`, `move_down()` (zmieniają row, nie wychodzą poza 0-2), `move_forward()` (zwraca nową kolumnę `col+1`, nie modyfikuje stanu), `reset(col, row)`. Może też sprawdzać kolizję, ale lepiej pozostawić to silnikowi.

#### 4. `models/fog_of_war.py`
- Klasa `FogOfWar` – przechowuje `discovered: list[list[bool]]` (30×3). Metoda `update(current_col, current_row)` ustawia wszystkie `discovered[col][row] = True` dla `col <= current_col` oraz dla `col = current_col + 1` (jeśli istnieje). Metoda `reset()` czyści tablicę i ustawia tylko kolumny 0 i 1 jako odkryte (zgodnie z początkowym stanem). `is_discovered(col, row) -> bool`.

#### 5. `managers/lives_manager.py`
- Klasa `LivesManager` – atrybut `lives` (int). Metody: `lose_life()`, `reset()`, `is_alive()`. Emituje zdarzenie (można użyć prostego `callback` lub `Observer`). Dla testów – można podczepić funkcję.

#### 6. `managers/score_manager.py`
- Klasa `ScoreManager` – atrybut `score`. Metody: `add_points(amount)`, `reset()`. Emituje zdarzenia.

#### 7. `challenges/challenge.py`
- Klasa abstrakcyjna `Challenge` z polami: `question: str`, `correct_answer: str`. Metoda abstrakcyjna `check_answer(user_input: str) -> bool`.
- `MultipleChoiceChallenge` dziedziczy, dodatkowe pole `options: list[str]` (trzy opcje). Metoda `check_answer` porównuje z poprawną.
- `TextChallenge` – sprawdza odpowiedź (case-insensitive, bez zbędnych spacji).

#### 8. `challenges/challenge_loader.py`
- Klasa `ChallengeLoader` z metodą `load_from_json(filepath: str) -> list[Challenge]`. Parsuje plik. Przykładowy JSON:
```json
[
  {
    "question": "Ile to 2+2?",
    "answerA": "3",
    "answerB": "4",
    "answerC": "5"
  },
  {
    "question": "Jaki kolor ma niebo?",
    "answerA": "niebieski",
    "answerB": "",
    "answerC": ""
  }
]
```
Gdy `answerB` i `answerC` puste – tworzy `TextChallenge` z poprawną odpowiedzią z `answerA`. W przeciwnym razie – `MultipleChoiceChallenge` z opcjami [answerA, answerB, answerC] i poprawną = answerA (zakładamy, że pierwsza opcja jest poprawna). Można też dodać pole `correct` – ale upraszczamy.

#### 9. `managers/challenge_manager.py`
- Klasa `ChallengeManager` – atrybuty: lista `challenges`, lista `wrong_answers` (lista krotek: pytanie, odpowiedź gracza, poprawna odpowiedź). Metoda `present_challenge(game_view)` – losuje pytanie, tworzy modal (widok), blokuje grę, zbiera odpowiedź, po odpowiedzi aktualizuje punkty/życia przez callbacki, zapisuje błędy, zwalnia blokadę. W Arcade najlepiej zrobić to przez zmianę widoku na `ChallengeView` i po odpowiedzi powrót.

#### 10. `views/start_view.py`, `game_view.py`, `challenge_view.py`, `victory_view.py`, `game_over_view.py`
- Wszystkie dziedziczą po `arcade.View`. 
- `GameView` – główna logika gry, rysowanie siatki, obsługa klawiszy (on_key_press). Przechowuje referencje do `GameGrid`, `Rocket`, `FogOfWar`, `LivesManager`, `ScoreManager`, `ChallengeManager`. W `on_update` sprawdza kolizje i ewentualne zwycięstwo.
- `ChallengeView` – wyświetla pytanie, opcje/pole tekstowe, przyciski (lub nasłuch na klawisze 1-3 i Enter). Po udzieleniu odpowiedzi zwraca wynik do `GameView` (np. przez callback).
- `VictoryView` – wyświetla punkty i listę błędnych odpowiedzi, przycisk „Nowa gra”.
- `GameOverView` – informacja o przegranej, przycisk powrotu do startu.

#### 11. `managers/ui_manager.py` (opcjonalnie, może być w widoku)
- Subskrybuje zmiany lives/score i aktualizuje tekst na ekranie. W Arcade można po prostu w `GameView.draw` wyświetlić aktualne wartości, ale dla osobności – osobna klasa.

#### 12. `main.py`
- Uruchamia `arcade.Window`, ustawia `StartView`.

### Testy (pytest)

Napisz testy jednostkowe dla:
- `MazeGenerator` – czy w każdej kolumnie 1–28 max 1 przeszkoda, czy start i meta puste, czy ścieżka jest wolna.
- `LivesManager` – utrata życia, reset, nie schodzi poniżej 0.
- `ScoreManager` – dodawanie punktów.
- `FogOfWar` – poprawna aktualizacja i reset.
- `Rocket` – blokada ruchu, move_forward nie zmienia stanu.
- `Challenge` – sprawdzanie odpowiedzi.
- `ChallengeLoader` – parsowanie JSON.

Przykład testu (pytest):

```python
def test_lives_manager_lose_life():
    lm = LivesManager()
    assert lm.lives == 3
    lm.lose_life()
    assert lm.lives == 2
    callback = Mock()
    lm.on_life_lost(callback)   # jeśli implementujesz obserwatora
    lm.lose_life()
    callback.assert_called_once_with(1)   # pozostałe życia
```

Test integracyjny: symulacja `GameView` z użyciem `arcade` (można użyć `unittest.mock` do mockowania `on_update` i zdarzeń klawiszy) – sprawdź, czy po ruchu w prawo na puste pole zwiększa się kolumna, a po wejściu na przeszkodę spada życie i reset pozycji.

### Uwagi implementacyjne dla Arcade

- Okno: np. 1200×600 (30 kolumn × 40px = 1200, 3 wiersze × 40 = 120, plus marginesy). Ustaw tytuł "Edukacyjna gra rakietą".
- Obsługa przycisków w `ChallengeView`: można użyć `arcade.gui.UIManager` i przycisków, albo prostsze – nasłuch na klawisze numeryczne i `Enter`. Dla pola tekstowego – `arcade.gui.UIInputText`.
- Blokada sterowania: `GameView.disabled = True` podczas challenge.
- Prawdopodobieństwo 20%: użyj `random.random() < 0.2`.
- Zapamiętanie błędnych odpowiedzi: `ChallengeManager.wrong_answers` – lista słowników lub krotek. Przekazana do `VictoryView`.

### Przykładowy szkielet `GameView`

```python
class GameView(arcade.View):
    def __init__(self, start_row, goal_row):
        super().__init__()
        self.grid = GameGrid(MazeGenerator.generate(start_row, goal_row))
        self.rocket = Rocket(col=0, row=start_row)
        self.fog = FogOfWar()
        self.fog.update(0, start_row)
        self.lives = LivesManager()
        self.score = ScoreManager()
        self.challenge_mgr = ChallengeManager("questions.json")
        self.challenge_active = False
        # ...

    def on_key_press(self, key, modifiers):
        if self.challenge_active:
            return
        if key == arcade.key.RIGHT:
            self._move_forward()
        elif key == arcade.key.UP:
            self.rocket.move_up()
        elif key == arcade.key.DOWN:
            self.rocket.move_down()
        # aktualizacja fog of war po ruchu
        self.fog.update(self.rocket.col, self.rocket.row)

    def _move_forward(self):
        next_col = self.rocket.col + 1
        if next_col >= 30:
            return
        if self.grid.get_cell(next_col, self.rocket.row) == 'obstacle':
            self.lives.lose_life()
            if not self.lives.is_alive():
                self.window.show_view(GameOverView())
            else:
                self.rocket.reset(0, self.start_row)
                self.fog.reset()
                self.fog.update(0, self.start_row)
        elif self.grid.get_cell(next_col, self.rocket.row) == 'goal':
            self.window.show_view(VictoryView(self.score.score, self.challenge_mgr.wrong_answers))
        else:
            self.rocket.move_forward()
            self.fog.update(self.rocket.col, self.rocket.row)
            if random.random() < 0.2:
                self._start_challenge()
```

### Oczekiwany wynik

Kompletny kod źródłowy (struktura katalogów z plikami `.py`), plik `questions.json`, testy oraz instrukcja uruchomienia:
- `pip install arcade pytest`
- `python main.py`
- `pytest tests/`

Upewnij się, że gra działa płynnie, nie ma wycieków pamięci, a interakcje są intuicyjne dla dziecka.

---

**To wszystko. Wykonaj zadanie zgodnie z powyższą specyfikacją.**