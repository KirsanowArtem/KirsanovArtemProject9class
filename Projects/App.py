import tkinter as tk
import random
from functools import partial
import webbrowser
import time


# =-=-=-= СТВОРЕННЯ КЛАСУ =-=-=-=
class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Морський бій")
        self.root.geometry("550x650")
        self.root.resizable(False, False)

        self.symbols = {
            'water': '🌊',
            'hit': '💥',
            'miss': '•',
            'dead': '❌'
        }

        self.show_menu()

    # =-=-=-= ІНІЦІАЛІЗАЦІЯ ГРИ =-=-=-=
    def setup(self):
        self.size = 10
        self.ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.hits = 0
        self.miss = 0
        self.dead = 0
        self.all_ships = sum(self.ships)
        self.start_time = 0
        self.playing = True

        # Ігрові поля
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.shots = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]

        self.make_ships()

    # =-=-=-= ГОЛОВНЕ МЕНЮ =-=-=-=
    def show_menu(self):
        # Останавливаем игру и таймер перед переходом в меню
        self.playing = False

        # Очищаем экран
        self.clear()

        # Заголовок
        title = tk.Label(self.root, text="Морський Бій", font=("Arial", 24, "bold"))
        title.pack(pady=30)

        # Кнопка Гри
        play = tk.Button(
            self.root,
            text="🎮 Грати",
            font=("Arial", 16),
            command=self.start,
            bg="#4CAF50",
            fg="white"
        )
        play.pack(pady=10, ipadx=30, ipady=10)

        # Кнопка Правил
        rules = tk.Button(
            self.root,
            text="📜 Правила",
            font=("Arial", 16),
            command=self.show_rules,
            bg="#2196F3",
            fg="white"
        )
        rules.pack(pady=10, ipadx=30, ipady=10)

        # Кнопка Інформації
        info = tk.Button(
            self.root,
            text="ℹ️ Інформація",
            font=("Arial", 16),
            command=self.show_info,
            bg="#607D8B",
            fg="white"
        )
        info.pack(pady=10, ipadx=30, ipady=10)

    def update_time(self):
        if not self.playing:
            return
        if not hasattr(self, 'time') or not self.time.winfo_exists():
            return

        try:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.time.config(text=f"Час: {minutes:02d}:{seconds:02d}")
            if self.playing:
                self.root.after(1000, self.update_time)
        except:
            return

    # =-=-=-= ВІКНО ПРАВИЛ =-=-=-=
    def show_rules(self):
        self.clear()
        rules_text = """
        Правила Морського бою:

        1. Гра ведеться на полі 10×10
        2. У кожного гравця є кораблі:
           - 1 корабель — 4 клітинки
           - 2 кораблі — 3 клітинки
           - 3 кораблі — 2 клітинки
           - 4 кораблі — 1 клітинка
        3. Кораблі не можуть торкатися один одного
        4. Гравець робить постріли, клікаючи по клітинкам
        5. Мета — першим знищити всі кораблі противника

        Позначення:
        🌊 - вода (ще не стріляли)
         • - промах
        💥 - попадання
        ❌ - знищений корабель
        """

        frame = tk.Frame(self.root)
        frame.pack(pady=20, padx=20)

        label = tk.Label(
            frame,
            text=rules_text,
            font=("Arial", 12),
            justify="left"
        )
        label.pack()

        # Кнопка повернення в меню
        back = tk.Button(
            self.root,
            text="← Назад",
            font=("Arial", 14),
            command=self.show_menu,
            bg="#9E9E9E",
            fg="white"
        )
        back.pack(pady=20)

    # =-=-=-= ВІКНО ІНФОРМАЦІЇ =-=-=-=
    def show_info(self):
        self.clear()

        frame = tk.Frame(self.root)
        frame.pack(pady=40)

        label = tk.Label(
            frame,
            text="Додаткова інформація:",
            font=("Arial", 22)
        )
        label.pack(pady=10)

        button_frame1 = tk.Frame(frame)
        button_frame1.pack(pady=10)

        go1 = tk.Button(
            button_frame1,
            text="Перейти на Код програми →",
            font=("Arial", 14),
            command=lambda: webbrowser.open("https://github.com/KirsanowArtem/KirsanovArtemProject9class/blob/main/Projects/App.py"),
            bg="#2196F3",
            fg="white"
        )
        go1.pack(side=tk.LEFT, padx=10)

        button_frame2 = tk.Frame(frame)
        button_frame2.pack(pady=10)

        go2 = tk.Button(
            button_frame2,
            text="Завантажити програму →",
            font=("Arial", 14),
            command=lambda: webbrowser.open(
                "https://drive.google.com/drive/folders/1bv1z5TjmJvKBxCHejtbP6wfkBisIZzQD?usp=sharing"),
            bg="#2196F3",
            fg="white"
        )
        go2.pack(side=tk.LEFT, padx=10)

        button_frame3 = tk.Frame(frame)
        button_frame3.pack(pady=10)

        go3 = tk.Button(
            button_frame3,
            text="Презентація →",
            font=("Arial", 14),
            command=lambda: webbrowser.open(
                "https://docs.google.com/presentation/d/1Oxf46naBlp-bQ7loUpDzCnZ0415qihTb/edit?usp=sharing&ouid=101339484759200254768&rtpof=true&sd=true"),
            bg="#2196F3",
            fg="white"
        )
        go3.pack(side=tk.LEFT, padx=10)

        button_frame4 = tk.Frame(frame)
        button_frame4.pack(pady=10)

        go4 = tk.Button(
            button_frame4,
            text="Зворотній зв'язок →",
            font=("Arial", 14),
            command=lambda: webbrowser.open(
                "https://t.me/ArtemKirss"),
            bg="#2196F3",
            fg="white"
        )
        go4.pack(side=tk.LEFT, padx=10)

        back = tk.Button(
            self.root,
            text="← Назад",
            font=("Arial", 14),
            command=self.show_menu,
            bg="#9E9E9E",
            fg="white"
        )
        back.pack(pady=10)

    # =-=-=-= ПОЧАТОК ГРИ =-=-=-=
    def start(self):
        self.setup()
        self.clear()
        self.make_board()
        self.start_time = time.time()

    def make_board(self):
        # Панель керування
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, pady=10, padx=10)

        # Кнопка меню
        menu = tk.Button(
            top,
            text="≡ Меню",
            font=("Arial", 12),
            command=self.show_menu,
            bg="#9E9E9E",
            fg="white"
        )
        menu.pack(side=tk.LEFT, padx=5)

        # Кнопка рестарту
        reset = tk.Button(
            top,
            text="↻ Рестарт",
            font=("Arial", 12),
            command=self.start,
            bg="#FF9800",
            fg="white"
        )
        reset.pack(side=tk.LEFT, padx=5)

        # Час
        self.time = tk.Label(
            top,
            text="Час: 00:00",
            font=('Arial', 12)
        )
        self.time.pack(side=tk.LEFT, expand=True)

        # Статистика
        self.score = tk.Label(
            top,
            text=f"🔴 {self.hits:02d}  ⚪ {self.miss:02d}  💀 {self.dead:02d}/{len(self.ships):02d}",
            font=('Arial', 12)
        )
        self.score.pack(side=tk.RIGHT)

        # Ігрове поле
        board = tk.Frame(self.root)
        board.pack(pady=10)

        for y in range(self.size):
            for x in range(self.size):
                btn = tk.Button(
                    board,
                    text=self.symbols['water'],
                    font=('Arial', 16),
                    width=2,
                    height=1,
                    command=partial(self.shoot, x, y),
                    bg="#BBDEFB"
                )
                btn.grid(row=y, column=x, padx=1, pady=1)
                self.buttons[y][x] = btn

        # Повідомлення про перемогу
        self.win = tk.Label(
            self.root,
            text="",
            font=("Arial", 16, "bold"),
            fg="#4CAF50"
        )
        self.win.pack(pady=10)

        # Запуск таймера
        self.update_time()

    def shoot(self, x, y):
        if not self.playing or self.shots[y][x] != 0:
            return

        if self.grid[y][x] == 1:
            self.shots[y][x] = 2
            self.buttons[y][x].config(text=self.symbols['hit'], bg="#FFCDD2")
            self.hits += 1

            if self.check_sunk(x, y):
                self.mark_sunk(x, y)
                self.dead += 1

            if self.dead == len(self.ships):
                self.playing = False
                elapsed = int(time.time() - self.start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                self.win.config(
                    text=f"ПЕРЕМОГА! Час: {minutes:02d}:{seconds:02d}\n" +
                         f"Попадань: {self.hits} | Промахів: {self.miss}"
                )
        else:
            self.shots[y][x] = 1  # Промах
            self.buttons[y][x].config(text=self.symbols['miss'], bg="#E0E0E0")
            self.miss += 1

        self.update_score()

    def update_score(self): # Оновлення статистики
        self.score.config(
            text=f"🔴 {self.hits:02d}  ⚪ {self.miss:02d}  💀 {self.dead:02d}/{len(self.ships):02d}"
        )

    # =-=-=-= ЛОГІКА ГРИ =-=-=-=
    def make_ships(self):
        for size in self.ships: # Генерація кораблів
            placed = False
            while not placed:
                dir = random.randint(0, 1)  # 0 - горизонтально, 1 - вертикально

                if dir == 0:  # Горизонтально
                    max_x = self.size - size
                    max_y = self.size
                    x = random.randint(0, max_x)
                    y = random.randint(0, max_y - 1)

                    if self.can_place(x, y, size, dir):
                        for i in range(size):
                            self.grid[y][x + i] = 1
                        placed = True

                else:  # Вертикально
                    max_x = self.size
                    max_y = self.size - size
                    x = random.randint(0, max_x - 1)
                    y = random.randint(0, max_y)

                    if self.can_place(x, y, size, dir):
                        for i in range(size):
                            self.grid[y + i][x] = 1
                        placed = True

    def can_place(self, x, y, size, dir): # Перевірка розміщення
        for i in range(size):
            if dir == 0:  # Горизонтально
                if self.grid[y][x + i] == 1:
                    return False
            else:  # Вертикально
                if self.grid[y + i][x] == 1:
                    return False

            # Перевірка сусідніх клітинок
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dir == 0:
                        nx, ny = x + i + dx, y + dy
                    else:
                        nx, ny = x + dx, y + i + dy

                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.grid[ny][nx] == 1:
                            return False
        return True

    def check_sunk(self, x, y): # Перевірка знищення корабля
        cells = []
        seen = set()
        queue = [(x, y)]

        while queue:
            cx, cy = queue.pop()
            if (cx, cy) in seen:
                continue
            seen.add((cx, cy))

            if 0 <= cx < self.size and 0 <= cy < self.size and self.grid[cy][cx] == 1:
                cells.append((cx, cy))
                queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])

        return all(self.shots[cy][cx] == 2 for cx, cy in cells)

    def mark_sunk(self, x, y): # Перевірка всіх клітинок знищеного корабля
        cells = []
        seen = set()
        queue = [(x, y)]

        while queue:
            cx, cy = queue.pop()
            if (cx, cy) in seen:
                continue
            seen.add((cx, cy))

            if 0 <= cx < self.size and 0 <= cy < self.size and self.grid[cy][cx] == 1:
                cells.append((cx, cy))
                queue.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])

        for cx, cy in cells:
            self.buttons[cy][cx].config(text=self.symbols['dead'], bg="#FF8A80")

    # =-=-=-= ДОПОМІЖНІ ФУНКЦІЇ =-=-=-=
    def clear(self): # Очищення вікна
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()