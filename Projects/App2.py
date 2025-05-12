import tkinter as tk
import random
from functools import partial
import webbrowser
import time
from collections import defaultdict
from PIL import Image, ImageTk
from colorsys import rgb_to_hls, hls_to_rgb
import re


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Морський бій")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)

        # Налаштування символів та кольорів
        self.symbols = {
            'water': '🌊',
            'hit': '💥',
            'miss': '•',
            'dead': '❌',
            'ship': '⬛'
        }

        self.colors = {
            'water': '#BBDEFB',
            'hit': '#FF5252',
            'miss': '#E0E0E0',
            'dead': '#FF5252',
            'ship': '#90CAF9',
            'last_move': '#FFA726',
            'selected': '#43A047',
            'text': '#333333',
            'bg': '#F5F5F5'
        }

        # Розміри кораблів
        self.ship_sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.available_ships = self.ship_sizes.copy()
        self.current_ship = None
        self.placing_ships = False
        self.player_turn = True

        # Ініціалізація змінних гри
        self.setup_variables()

        # Налаштування стилю
        self.root.configure(bg=self.colors['bg'])

        self.load_images()

        self.show_menu()

    def setup_variables(self):
        """Ініціалізація змінних гри"""
        self.size = 10
        self.player_hits = 0
        self.player_miss = 0
        self.player_dead = 0
        self.computer_hits = 0
        self.computer_miss = 0
        self.computer_dead = 0
        self.player_destroyed = defaultdict(int)
        self.computer_destroyed = defaultdict(int)
        self.computer_targets = []
        self.computer_hit_cells = []
        self.start_time = 0
        self.playing = False
        self.placing_ships = True
        self.last_player_move = None
        self.last_computer_move = None
        self.selected_ship = None

        self.available_ships = self.ship_sizes.copy()

        # Ігрові поля
        self.player_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.computer_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]

        # Масиви пострілів
        self.player_shots = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.computer_shots = [[0 for _ in range(self.size)] for _ in range(self.size)]

        # Списки кораблів
        self.player_ships = []
        self.computer_ships = []

        # Кнопки
        self.player_buttons = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.computer_buttons = [[None for _ in range(self.size)] for _ in range(self.size)]

    def load_images(self):
        """Завантаження зображень для анімацій"""
        try:
            self.explosion_img = Image.open("explosion.png").resize((40, 40))
            self.explosion_photo = ImageTk.PhotoImage(self.explosion_img)
        except:
            self.explosion_photo = None

    # ==================== МЕНЮ ТА ІНТЕРФЕЙС ====================

    def show_menu(self):
        """Показати головне меню"""
        self.clear()
        self.setup_variables()

        # Заголовок
        title_frame = tk.Frame(self.root, bg=self.colors['bg'])
        title_frame.pack(pady=30)

        title = tk.Label(
            title_frame,
            text="Морський Бій",
            font=("Arial", 36, "bold"),
            fg=self.colors['text'],
            bg=self.colors['bg']
        )
        title.pack()

        # Кнопки меню
        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.pack(pady=30)

        buttons = [
            ("🎮 Грати", self.start_game, "#4CAF50"),
            ("📜 Правила", self.show_rules, "#2196F3"),
            ("ℹ️ Інформація", self.show_info, "#607D8B")
        ]

        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 18),
                command=command,
                bg=color,
                fg="white",
                padx=20,
                pady=10,
                bd=0,
                relief=tk.FLAT,
                activebackground=color,
                activeforeground="white"
            )
            btn.pack(pady=10, ipadx=10, ipady=5)
            btn.bind("<Enter>", partial(self.on_button_enter, btn))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

    def lighter_color(self, color, amount=30):
        """Зробити колір світлішим"""
        r, g, b = [int(x, 16) for x in re.match(r'#(..)(..)(..)', color).groups()]
        h, l, s = rgb_to_hls(r / 255, g / 255, b / 255)
        l = min(1, l * (1 + amount / 100))
        r, g, b = hls_to_rgb(h, l, s)
        return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

    def show_rules(self):
        """Показати правила гри"""
        self.clear()

        frame = tk.Frame(self.root, bg=self.colors['bg'])
        frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        title = tk.Label(
            scrollable_frame,
            text="Правила Морського бою",
            font=("Arial", 20, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title.pack(pady=20)
        rules_text = [
            ("1. Гра ведеться на двох полях 10×10 (ваше і противника)", 14),
            ("2. У кожного гравця є кораблі:", 14),
            ("   - 1 корабель — 4 клітинки", 12),
            ("   - 2 кораблі — 3 клітинки", 12),
            ("   - 3 кораблі — 2 клітинки", 12),
            ("   - 4 кораблі — 1 клітинка", 12),
            ("3. Кораблі не можуть торкатися один одного (ні сторонами, ні кутами)", 14),
            ("4. Гравець і комп'ютер ходять по черзі", 14),
            ("5. Якщо гравець/комп'ютер потрапляє у корабель, він робить ще один хід", 14),
            ("6. Мета — першим знищити всі кораблі противника", 14),
            ("", 14),
            ("Позначення (шрифт emoji для кращого відображення):", 16),
            ("🌊 - вода (ще не стріляли)", 12),
            ("• - промах", 12),
            ("💥 - попадання (червоний колір)", 12),
            ("❌ - знищений корабель (червоний колір)", 12),
            ("⬛ - ваш корабель (під час розстановки зелений колір)", 12),
            ("Керування", 16),
            ("←, →, ↑, ↓ або A, D, W, S - переміщення корабля при роззміщенні", 12),
            ("Ctrl або Q - переворот корабля при роззміщенні", 12),
            ("Lcm - натискання на кнопки, розміщення корабля, постріл", 12),
        ]

        for text, size in rules_text:
            label = tk.Label(
                scrollable_frame,
                text=text,
                font=("Arial", size),
                bg=self.colors['bg'],
                fg=self.colors['text'],
                justify="left",
                anchor="w"
            )
            label.pack(fill=tk.X, padx=20, pady=2)

        # Кнопка назад
        back = tk.Button(
            scrollable_frame,
            text="← Назад",
            font=("Arial", 14),
            command=self.show_menu,
            bg="#9E9E9E",
            fg="white",
            bd=0,
            padx=20,
            pady=10,
            activebackground="#9E9E9E",
            activeforeground="white"
        )
        back.pack(pady=20)
        back.bind("<Enter>", lambda e: back.config(bg=self.lighter_color("#9E9E9E")))
        back.bind("<Leave>", lambda e: back.config(bg="#9E9E9E"))

    def show_info(self):
        """Показати інформаційне меню"""
        self.clear()

        frame = tk.Frame(self.root, bg=self.colors['bg'])
        frame.pack(pady=40, fill=tk.BOTH, expand=True)

        title = tk.Label(
            frame,
            text="Додаткова інформація:",
            font=("Arial", 24),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title.pack(pady=20)

        # Кнопки посилань
        links = [
            ("Перейти на Код програми →",
             "https://github.com/KirsanowArtem/KirsanovArtemProject9Class/blob/main/Projects/App.py"),
            ("Завантажити програму →",
             "https://drive.google.com/drive/folders/1bv1z5TjmJvKBxCHejtbP6wfkBisIZzQD?usp=sharing"),
            ("Презентація →",
             "https://docs.google.com/presentation/d/1Oxf46naBlp-bQ7loUpDzCnZ0415qihTb/edit?usp=sharing&ouid=101339484759200254768&rtpof=true&sd=true"),
            ("Зворотній зв'язок →",
             "https://t.me/ArtemKirss")
        ]

        for text, url in links:
            btn_frame = tk.Frame(frame, bg=self.colors['bg'])
            btn_frame.pack(pady=10)

            btn = tk.Button(
                btn_frame,
                text=text,
                font=("Arial", 14),
                command=lambda u=url: webbrowser.open(u),
                bg="#2196F3",
                fg="white",
                bd=0,
                padx=20,
                pady=10,
                activebackground="#2196F3",
                activeforeground="white"
            )
            btn.pack(side=tk.LEFT, padx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.lighter_color("#2196F3")))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2196F3"))

            # Кнопка назад
            back = tk.Button(
                frame,
                text="← Назад",
                font=("Arial", 14),
                command=self.show_menu,
                bg="#9E9E9E",
                fg="white",
                bd=0,
                padx=20,
                pady=10,
                activebackground="#9E9E9E",
                activeforeground="white"
            )
        back.pack(pady=20)
        back.bind("<Enter>", lambda e: back.config(bg=self.lighter_color("#9E9E9E")))
        back.bind("<Leave>", lambda e: back.config(bg="#9E9E9E"))

        # ==================== ІГРОВИЙ ПРОЦЕС ====================

    def start(self):
        def start(self):
            """Почати нову гру"""
            self.setup_variables()
            self.clear()

            self.placing_ships = True
            self.player_turn = True
            self.available_ships = self.ship_sizes.copy()

            self.make_boards()
            self.make_computer_ships()
            self.show_ship_selection()

            self.start_time = time.time()
            self.playing = True
            self.update_time()

    def start_game(self):
        """Запуск новой игры с проверкой всех состояний"""
        try:
            self.setup_variables()

            self.placing_ships = True
            self.player_turn = True
            self.playing = True
            self.available_ships = self.ship_sizes.copy()

            self.clear()

            self.make_boards()
            self.make_computer_ships()
            self.show_ship_selection()

            self.start_time = time.time()
            self.update_time()

        except Exception as e:
            print(f"Ошибка при запуске игры: {e}")
            error_label = tk.Label(
                self.root,
                text="Помилка при запуску гри! Спробуйте ще раз.",
                font=("Arial", 14),
                fg="#FF0000",
                bg=self.colors['bg']
            )
            error_label.pack(pady=20)

            retry_btn = tk.Button(
                self.root,
                text="Спробувати знову",
                command=self.start_game,
                bg="#4CAF50",
                fg="white",
                font=("Arial", 12),
                padx=15,
                pady=5
            )
            retry_btn.pack(pady=10)

    def make_boards(self):
        """Генерація ігрових досок"""
        top = tk.Frame(self.root, bg=self.colors['bg'])
        top.pack(fill=tk.X, pady=10, padx=10)

        buttons = [
            ("≡ Меню", self.show_menu, "#9E9E9E"),
            ("↻ Рестарт", self.start_game, "#FF9800")
        ]

        for text, command, color in buttons:
            btn = tk.Button(
                top,
                text=text,
                font=("Arial", 12),
                command=command,
                bg=color,
                fg="white",
                bd=0,
                padx=10,
                pady=5,
                activebackground=color,
                activeforeground="white"
            )
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind("<Enter>", partial(self.on_button_enter, btn))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

        # Таймер
        self.time_label = tk.Label(
            top,
            text="Час: 00:00",
            font=('Arial', 12),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        self.time_label.pack(side=tk.RIGHT, padx=10)

        boards_frame = tk.Frame(self.root, bg=self.colors['bg'])
        boards_frame.pack(pady=10)

        # Лічильники
        self.left_counter = tk.Frame(boards_frame, bg=self.colors['bg'])
        self.left_counter.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        computer_counter_label = tk.Label(
            self.left_counter,
            text="Комп'ютер:",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        computer_counter_label.pack()

        self.computer_counter_text = tk.StringVar()
        self.computer_counter = tk.Label(
            self.left_counter,
            textvariable=self.computer_counter_text,
            font=("Arial", 10),
            justify=tk.LEFT,
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        self.computer_counter.pack()

        # Доска ігрока
        player_frame = tk.Frame(boards_frame, bg=self.colors['bg'])
        player_frame.pack(side=tk.LEFT, padx=20)

        player_label = tk.Label(
            player_frame,
            text="Ваше поле",
            font=("Arial", 14, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        player_label.pack()

        self.player_board = tk.Frame(player_frame, bg=self.colors['bg'])
        self.player_board.pack()

        self.player_buttons = [[None for _ in range(self.size)] for _ in range(self.size)]
        for y in range(self.size):
            for x in range(self.size):
                btn = tk.Button(
                    self.player_board,
                    text=self.symbols['water'],
                    font=('Arial', 16),
                    width=2,
                    height=1,
                    command=partial(self.player_board_click, x, y),
                    bg=self.colors['water'],
                    activebackground=self.colors['water'],
                    bd=1,
                    relief=tk.RAISED
                )
                btn.grid(row=y, column=x, padx=1, pady=1)
                self.player_buttons[y][x] = btn

        computer_frame = tk.Frame(boards_frame, bg=self.colors['bg'])
        computer_frame.pack(side=tk.LEFT, padx=20)

        computer_label = tk.Label(
            computer_frame,
            text="Поле противника",
            font=("Arial", 14, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        computer_label.pack()

        self.computer_board = tk.Frame(computer_frame, bg=self.colors['bg'])
        self.computer_board.pack()

        self.computer_buttons = [[None for _ in range(self.size)] for _ in range(self.size)]
        for y in range(self.size):
            for x in range(self.size):
                btn = tk.Button(
                    self.computer_board,
                    text=self.symbols['water'],
                    font=('Arial', 16),
                    width=2,
                    height=1,
                    command=None if self.placing_ships else partial(self.player_shoot, x, y),
                    bg=self.colors['water'],
                    activebackground=self.colors['water'],
                    bd=1,
                    relief=tk.RAISED
                )
                btn.grid(row=y, column=x, padx=1, pady=1)
                self.computer_buttons[y][x] = btn

        # Лічильник гравця
        self.right_counter = tk.Frame(boards_frame, bg=self.colors['bg'])
        self.right_counter.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        player_counter_label = tk.Label(
            self.right_counter,
            text="Ви:",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        player_counter_label.pack()

        self.player_counter_text = tk.StringVar()
        self.player_counter = tk.Label(
            self.right_counter,
            textvariable=self.player_counter_text,
            font=("Arial", 10),
            justify=tk.LEFT,
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        self.player_counter.pack()

        self.message = tk.Label(
            self.root,
            text="",
            font=("Arial", 14),
            fg="#4CAF50",
            bg=self.colors['bg']
        )
        self.message.pack(pady=10)

        if self.placing_ships:
            self.controls_frame = tk.Frame(self.root, bg=self.colors['bg'])
            self.controls_frame.pack(pady=10)

            buttons = [
                ("Авторастановка", self.auto_place_ships, "#2196F3"),
                ("Завершити розстановку", self.finish_placing, "#4CAF50")
            ]

            for text, command, color in buttons:
                btn = tk.Button(
                    self.controls_frame,
                    text=text,
                    font=("Arial", 12),
                    command=command,
                    bg=color,
                    fg="white",
                    bd=0,
                    padx=15,
                    pady=8,
                    activebackground=color,
                    activeforeground="white"
                )
                btn.pack(side=tk.LEFT, padx=5)
                btn.bind("<Enter>", partial(self.on_button_enter, btn))
                btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

            self.finish_btn = self.controls_frame.winfo_children()[-1]
            self.finish_btn.config(state=tk.DISABLED)

        self.update_counters()

    def update_time(self):
        """Оновити таймер гри"""
        if not self.playing:
            return

        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.time_label.config(text=f"Час: {minutes:02d}:{seconds:02d}")

        if self.playing:
            self.root.after(1000, self.update_time)

    def update_counters(self):
        """Оновити лічильники знищених кораблів"""
        player_text = "1п: {}/4\n2п: {}/3\n3п: {}/2\n4п: {}/1".format(
            self.player_destroyed[1],
            self.player_destroyed[2],
            self.player_destroyed[3],
            self.player_destroyed[4]
        )
        self.player_counter_text.set(player_text)

        computer_text = "1п: {}/4\n2п: {}/3\n3п: {}/2\n4п: {}/1".format(
            self.computer_destroyed[1],
            self.computer_destroyed[2],
            self.computer_destroyed[3],
            self.computer_destroyed[4]
        )
        self.computer_counter_text.set(computer_text)

    # ==================== РОЗСТАНОВКА КОРАБЛІВ ====================

    def show_ship_selection(self):
        """Показати панель вибору кораблів для розстановки"""
        self.ship_selection_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.ship_selection_frame.pack(pady=10)

        label = tk.Label(
            self.ship_selection_frame,
            text="Оберіть корабель для розстановки:",
            font=("Arial", 12),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        label.pack()

        self.ship_buttons_frame = tk.Frame(self.ship_selection_frame, bg=self.colors['bg'])
        self.ship_buttons_frame.pack()

        self.update_ship_buttons()

    def update_ship_buttons(self):
        """Оновити кнопки вибору кораблів"""
        for widget in self.ship_buttons_frame.winfo_children():
            widget.destroy()

        ship_counts = {}
        for size in self.available_ships:
            ship_counts[size] = ship_counts.get(size, 0) + 1

        for size in sorted(ship_counts.keys(), reverse=True):
            count = ship_counts[size]
            btn = tk.Button(
                self.ship_buttons_frame,
                text=f"{size} клітинок (x{count})",
                font=("Arial", 10),
                command=partial(self.select_ship, size),
                bg="#2196F3",
                fg="white",
                bd=0,
                padx=10,
                pady=5,
                activebackground="#2196F3",
                activeforeground="white"
            )
            btn.pack(side=tk.LEFT, padx=5)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.lighter_color("#2196F3")))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2196F3"))

    def select_ship(self, size):
        """Вибрати корабель для розміщення"""
        if hasattr(self, 'selected_ship') and self.selected_ship:
            for cell in self.selected_ship['cells']:
                cx, cy = cell
                self.player_buttons[cy][cx].config(bg=self.colors['ship'])

        self.current_ship = {
            'size': size,
            'direction': 0,  # 0 - горизонтально, 1 - вертикально
            'cells': []
        }
        self.message.config(
            text=f"Оберіть місце для корабля з {size} клітинок (WASD/стрілки - перемістити, Q/Ctrl - повернути)")

    def player_board_click(self, x, y):
        """Обробник кліку на дошку гравця"""
        if self.current_ship:
            self.place_ship(x, y)
        else:
            self.select_ship_to_move(x, y)

    def place_ship(self, x, y):
        """Розмістити корабель на дошці"""
        if not self.current_ship or not self.placing_ships:
            return

        size = self.current_ship['size']
        direction = self.current_ship['direction']

        # Знаходимо найближче доступне місце
        x, y = self.find_nearest_valid_position(x, y, size, direction)

        if x is None or y is None:
            self.message.config(text="Немає доступного місця для корабля такого розміру!")
            return

        if self.can_place_ship(x, y, size, direction, self.player_grid):
            # Знімаємо виділення з попереднього корабля
            if hasattr(self, 'selected_ship') and self.selected_ship:
                for cell in self.selected_ship['cells']:
                    cx, cy = cell
                    self.player_buttons[cy][cx].config(bg=self.colors['ship'])

            # Розміщуємо корабель
            cells = []
            for i in range(size):
                if direction == 0:  # Горизонтально
                    self.player_grid[y][x + i] = 1
                    self.player_buttons[y][x + i].config(
                        text=self.symbols['ship'],
                        bg=self.colors['selected']
                    )
                    cells.append((x + i, y))
                else:  # Вертикально
                    self.player_grid[y + i][x] = 1
                    self.player_buttons[y + i][x].config(
                        text=self.symbols['ship'],
                        bg=self.colors['selected']
                    )
                    cells.append((x, y + i))

            self.player_ships.append(cells)
            self.selected_ship = {
                'size': size,
                'direction': direction,
                'cells': cells.copy()
            }

            # Видаляємо розміщений корабель зі списку доступних
            if size in self.available_ships:
                self.available_ships.remove(size)

            # Оновлюємо кнопки вибору кораблів
            self.update_ship_buttons()

            # Скидаємо поточний корабель
            self.current_ship = None

            # Перевіряємо, чи всі кораблі розміщені
            if not self.available_ships:
                self.finish_btn.config(state=tk.NORMAL)
                self.message.config(text="Всі кораблі розміщено! Натисніть 'Завершити розстановку'")
            else:
                self.message.config(text="Оберіть наступний корабель для розміщення")
        else:
            self.message.config(text="Неможливо розмістити корабель тут!")

    def find_nearest_valid_position(self, x, y, size, direction):
        """Знайти найближчу доступну позицію для корабля"""
        if self.can_place_ship(x, y, size, direction, self.player_grid):
            return x, y

        for radius in range(1, self.size):
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if direction == 0 and nx + size <= self.size:
                            if self.can_place_ship(nx, ny, size, direction, self.player_grid):
                                return nx, ny
                        elif direction == 1 and ny + size <= self.size:
                            if self.can_place_ship(nx, ny, size, direction, self.player_grid):
                                return nx, ny

        return None, None

    def can_place_ship(self, x, y, size, direction, grid):
        """Перевірити, чи можна розмістити корабель"""
        if direction == 0:  # Горизонтально
            if x + size > self.size:
                return False
            for i in range(size):
                if grid[y][x + i] == 1:
                    return False
                # Перевіряємо сусідні клітинки
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + i + dx, y + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if grid[ny][nx] == 1:
                                return False
        else:  # Вертикально
            if y + size > self.size:
                return False
            for i in range(size):
                if grid[y + i][x] == 1:
                    return False
                # Перевіряємо сусідні клітинки
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        nx, ny = x + dx, y + i + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if grid[ny][nx] == 1:
                                return False
        return True

    def select_ship_to_move(self, x, y):
        """Вибрати корабель для переміщення"""
        if hasattr(self, 'selected_ship') and self.selected_ship:
            for cell in self.selected_ship['cells']:
                cx, cy = cell
                self.player_buttons[cy][cx].config(bg=self.colors['ship'])

        # Знаходимо корабель за координатами
        for ship in self.player_ships:
            if (x, y) in ship:
                self.selected_ship = {
                    'size': len(ship),
                    'direction': 0 if ship[0][0] != ship[-1][0] else 1,
                    'cells': ship.copy()
                }
                # Виділяємо корабель
                for cell in ship:
                    cx, cy = cell
                    self.player_buttons[cy][cx].config(bg=self.colors['selected'])
                self.message.config(
                    text=f"Корабель з {len(ship)} клітинок обрано (WASD/стрілки - перемістити, Q/Ctrl - повернути)")
                return

        self.selected_ship = None
        self.message.config(text="Оберіть корабель для переміщення")

    def move_ship(self, dx, dy):
        """Перемістити обраний корабель"""
        if not hasattr(self, 'selected_ship') or not self.selected_ship:
            return

        new_cells = []
        for cell in self.selected_ship['cells']:
            x, y = cell
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.size and 0 <= ny < self.size):
                self.message.config(text="Неможливо перемістити корабель за межі поля!")
                return
            new_cells.append((nx, ny))

        # Перевіряємо на перетин з іншими кораблями
        temp_grid = [row.copy() for row in self.player_grid]
        for cell in self.selected_ship['cells']:
            x, y = cell
            temp_grid[y][x] = 0

        for cell in new_cells:
            x, y = cell
            if temp_grid[y][x] == 1:
                self.message.config(text="Неможливо перемістити корабель - перетин з іншим кораблем!")
                return
            # Перевіряємо сусідні клітинки
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if temp_grid[ny][nx] == 1:
                            self.message.config(text="Неможливо перемістити корабель - поруч інший корабель!")
                            return

        # Переміщуємо корабель
        for cell in self.selected_ship['cells']:
            x, y = cell
            self.player_grid[y][x] = 0
            self.player_buttons[y][x].config(text=self.symbols['water'], bg=self.colors['water'])

        for i, cell in enumerate(new_cells):
            x, y = cell
            self.player_grid[y][x] = 1
            self.player_buttons[y][x].config(text=self.symbols['ship'], bg=self.colors['selected'])
            self.selected_ship['cells'][i] = (x, y)

        # Оновлюємо корабель у списку кораблів гравця
        for i, ship in enumerate(self.player_ships):
            if set(ship) == set(self.selected_ship['cells']):
                self.player_ships[i] = new_cells
                break

        self.message.config(text=f"Корабель переміщено (WASD/стрілки - перемістити, Q/Ctrl - повернути)")

    def rotate_selected_ship(self):
        """Повернути обраний корабель"""
        if not hasattr(self, 'selected_ship') or not self.selected_ship:
            return

        size = self.selected_ship['size']
        direction = 1 - self.selected_ship['direction']  # Змінюємо напрямок
        x, y = self.selected_ship['cells'][0]  # Беремо першу клітинку корабля

        # Перевіряємо, чи можна повернути корабель
        if direction == 0:  # Горизонтально
            if x + size > self.size:
                self.message.config(text="Неможливо повернути корабель - виходить за межі поля!")
                return
        else:  # Вертикально
            if y + size > self.size:
                self.message.config(text="Неможливо повернути корабель - виходить за межі поля!")
                return

        # Перевіряємо на перетин з іншими кораблями
        temp_grid = [row.copy() for row in self.player_grid]
        for cell in self.selected_ship['cells']:
            cx, cy = cell
            temp_grid[cy][cx] = 0

        new_cells = []
        for i in range(size):
            if direction == 0:  # Горизонтально
                nx, ny = x + i, y
            else:  # Вертикально
                nx, ny = x, y + i

            if not (0 <= nx < self.size and 0 <= ny < self.size):
                self.message.config(text="Неможливо повернути корабель - виходить за межі поля!")
                return

            if temp_grid[ny][nx] == 1:
                self.message.config(text="Неможливо повернути корабель - перетин з іншим кораблем!")
                return
            # Перевіряємо сусідні клітинки
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nnx, nny = nx + dx, ny + dy
                    if 0 <= nnx < self.size and 0 <= nny < self.size:
                        if temp_grid[nny][nnx] == 1:
                            self.message.config(text="Неможливо повернути корабель - поруч інший корабель!")
                            return
            new_cells.append((nx, ny))

        # Повертаємо корабель
        for cell in self.selected_ship['cells']:
            cx, cy = cell
            self.player_grid[cy][cx] = 0
            self.player_buttons[cy][cx].config(text=self.symbols['water'], bg=self.colors['water'])

        for i, (nx, ny) in enumerate(new_cells):
            self.player_grid[ny][nx] = 1
            self.player_buttons[ny][nx].config(text=self.symbols['ship'], bg=self.colors['selected'])
            self.selected_ship['cells'][i] = (nx, ny)

        self.selected_ship['direction'] = direction

        # Оновлюємо корабель у списку кораблів гравця
        for i, ship in enumerate(self.player_ships):
            if set(ship) == set(self.selected_ship['cells']):
                self.player_ships[i] = new_cells
                break

        self.message.config(text=f"Корабель повернуто (WASD/стрілки - перемістити, Q/Ctrl - повернути)")

    def auto_place_ships(self):
        """Автоматично розставити всі кораблі"""
        if not self.placing_ships:
            return

        # Очищаємо існуючі кораблі гравця
        for y in range(self.size):
            for x in range(self.size):
                if self.player_grid[y][x] == 1:
                    self.player_grid[y][x] = 0
                    self.player_buttons[y][x].config(text=self.symbols['water'], bg=self.colors['water'])

        self.player_ships = []
        self.available_ships = self.ship_sizes.copy()

        # Розміщуємо кораблі випадковим чином
        sizes = self.available_ships.copy()
        random.shuffle(sizes)

        for size in sizes:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                direction = random.randint(0, 1)

                if self.can_place_ship(x, y, size, direction, self.player_grid):
                    cells = []
                    for i in range(size):
                        if direction == 0:  # Горизонтально
                            self.player_grid[y][x + i] = 1
                            self.player_buttons[y][x + i].config(
                                text=self.symbols['ship'],
                                bg=self.colors['ship']
                            )
                            cells.append((x + i, y))
                        else:  # Вертикально
                            self.player_grid[y + i][x] = 1
                            self.player_buttons[y + i][x].config(
                                text=self.symbols['ship'],
                                bg=self.colors['ship']
                            )
                            cells.append((x, y + i))

                    self.player_ships.append(cells)
                    if size in self.available_ships:
                        self.available_ships.remove(size)
                    placed = True
                attempts += 1

        # Виділяємо останній розміщений корабель
        if self.player_ships:
            self.selected_ship = {
                'size': size,
                'direction': direction,
                'cells': cells.copy()
            }
            for cell in cells:
                cx, cy = cell
                self.player_buttons[cy][cx].config(bg=self.colors['selected'])

        self.update_ship_buttons()
        if not self.available_ships:
            self.finish_btn.config(state=tk.NORMAL)
            self.message.config(text="Всі кораблі розміщено! Натисніть 'Завершити розстановку'")
        else:
            self.message.config(text="Не всі кораблі вдалося розмістити автоматично. Дорозмістіть вручну.")

    def make_computer_ships(self):
        """Створити кораблі комп'ютера"""
        sizes = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

        for size in sizes:
            placed = False
            while not placed:
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                direction = random.randint(0, 1)  # 0 - горизонтально, 1 - вертикально

                if self.can_place_ship(x, y, size, direction, self.computer_grid):
                    cells = []
                    for i in range(size):
                        if direction == 0:  # Горизонтально
                            self.computer_grid[y][x + i] = 1
                            cells.append((x + i, y))
                        else:  # Вертикально
                            self.computer_grid[y + i][x] = 1
                            cells.append((x, y + i))

                    self.computer_ships.append(cells)
                    placed = True

    def finish_placing(self):
        """Завершить расстановку кораблей"""
        self.placing_ships = False
        self.playing = True
        self.player_turn = True

        if hasattr(self, 'selected_ship') and self.selected_ship:
            for cell in self.selected_ship['cells']:
                cx, cy = cell
                self.player_buttons[cy][cx].config(bg=self.colors['ship'])

        if hasattr(self, 'ship_selection_frame') and self.ship_selection_frame.winfo_exists():
            self.ship_selection_frame.destroy()

        if hasattr(self, 'controls_frame') and self.controls_frame.winfo_exists():
            self.controls_frame.destroy()

        for y in range(self.size):
            for x in range(self.size):
                self.computer_buttons[y][x].config(command=partial(self.player_shoot, x, y))

        self.message.config(text="Игра началась! Ваш ход.")

        self.start_time = time.time()
        self.update_time()

    # ==================== ІГРОВИЙ ПРОЦЕС ====================

    def player_shoot(self, x, y):
        """Обробник пострілу гравця"""
        if not self.playing or not self.player_turn or self.player_shots[y][x] != 0:
            return

        # Скидаємо підсвічування попереднього ходу гравця
        if self.last_player_move:
            lx, ly = self.last_player_move
            if self.player_shots[ly][lx] == 1:  # Промах
                self.computer_buttons[ly][lx].config(bg=self.colors['miss'])
            elif self.player_shots[ly][lx] == 2:  # Попадання
                self.computer_buttons[ly][lx].config(bg=self.colors['hit'])

        if self.computer_grid[y][x] == 1:
            self.player_shots[y][x] = 2  # Попадання
            self.computer_buttons[y][x].config(
                text=self.symbols['hit'],
                bg=self.colors['last_move']
            )
            self.player_hits += 1
            self.last_player_move = (x, y)

            # Перевіряємо, чи потоплений корабель
            sunk = False
            sunk_ship_size = 0
            for ship in self.computer_ships:
                if (x, y) in ship:
                    # Перевіряємо, чи всі клітинки корабля підбиті
                    if all(self.player_shots[cy][cx] == 2 for (cx, cy) in ship):
                        sunk = True
                        sunk_ship_size = len(ship)
                        self.computer_dead += 1
                        self.player_destroyed[sunk_ship_size] += 1
                        # Позначаємо корабель як потоплений
                        for cx, cy in ship:
                            if (cx, cy) == (x, y):
                                self.computer_buttons[cy][cx].config(
                                    text=self.symbols['dead'],
                                    bg=self.colors['last_move']
                                )
                            else:
                                self.computer_buttons[cy][cx].config(
                                    text=self.symbols['dead'],
                                    bg=self.colors['dead']
                                )
                            # Позначаємо клітинки навколо потопленого корабля
                            for dy in [-1, 0, 1]:
                                for dx in [-1, 0, 1]:
                                    nx, ny = cx + dx, cy + dy
                                    if 0 <= nx < self.size and 0 <= ny < self.size:
                                        if self.player_shots[ny][nx] == 0:
                                            self.player_shots[ny][nx] = 1
                                            self.computer_buttons[ny][nx].config(
                                                text=self.symbols['miss'],
                                                bg=self.colors['miss']
                                            )
                        break

            if sunk:
                self.message.config(text=f"Ви потопили {sunk_ship_size}-палубний корабель противника! Ходіть ще раз.")
            else:
                self.message.config(text=f"Ви влучили! Ходіть ще раз.")

            # Перевіряємо кінець гри
            if sum(self.player_destroyed.values()) == 10:
                self.game_over(True)
                return
        else:
            self.player_shots[y][x] = 1  # Промах
            self.computer_buttons[y][x].config(
                text=self.symbols['miss'],
                bg=self.colors['last_move']
            )
            self.player_miss += 1
            self.player_turn = False
            self.last_player_move = (x, y)
            self.message.config(text="Ви промахнулись. Хід противника.")
            self.root.after(1000, self.computer_turn)

        self.update_counters()

    def computer_turn(self):
        """Хід комп'ютера"""
        if not self.playing or self.player_turn:
            return

        # Скидаємо підсвічування попереднього ходу комп'ютера
        if self.last_computer_move:
            lx, ly = self.last_computer_move
            if self.computer_shots[ly][lx] == 1:  # Промах
                self.player_buttons[ly][lx].config(bg=self.colors['miss'])
            elif self.computer_shots[ly][lx] == 2:  # Попадання
                self.player_buttons[ly][lx].config(bg=self.colors['hit'])

        # Розумний алгоритм пострілу комп'ютера
        x, y = self.find_best_shot()

        if self.player_grid[y][x] == 1:
            self.computer_shots[y][x] = 2  # Попадання
            self.player_buttons[y][x].config(
                text=self.symbols['hit'],
                bg=self.colors['last_move']
            )
            self.computer_hits += 1
            self.last_computer_move = (x, y)
            self.computer_hit_cells.append((x, y))  # Додаємо попадання до списку

            # Перевіряємо, чи потоплений корабель
            sunk = False
            sunk_ship_size = 0
            for ship in self.player_ships:
                if (x, y) in ship:
                    # Перевіряємо, чи всі клітинки корабля підбиті
                    if all(self.computer_shots[cy][cx] == 2 for (cx, cy) in ship):
                        sunk = True
                        sunk_ship_size = len(ship)
                        self.computer_dead += 1
                        self.computer_destroyed[sunk_ship_size] += 1
                        # Позначаємо корабель як потоплений
                        for cx, cy in ship:
                            if (cx, cy) == (x, y):
                                self.player_buttons[cy][cx].config(
                                    text=self.symbols['dead'],
                                    bg=self.colors['last_move']
                                )
                            else:
                                self.player_buttons[cy][cx].config(
                                    text=self.symbols['dead'],
                                    bg=self.colors['dead']
                                )
                            # Позначаємо клітинки навколо потопленого корабля
                            for dy in [-1, 0, 1]:
                                for dx in [-1, 0, 1]:
                                    nx, ny = cx + dx, cy + dy
                                    if 0 <= nx < self.size and 0 <= ny < self.size:
                                        if self.computer_shots[ny][nx] == 0:
                                            self.computer_shots[ny][nx] = 1
                                            self.player_buttons[ny][nx].config(
                                                text=self.symbols['miss'],
                                                bg=self.colors['miss']
                                            )
                        # Видаляємо всі попадання по цьому кораблю зі списку цілей
                        self.computer_hit_cells = [cell for cell in self.computer_hit_cells if cell not in ship]
                        break

            if sunk:
                self.message.config(text=f"Противоник потопив ваш {sunk_ship_size}-палубний корабель! Його хід ще раз.")
            else:
                self.message.config(text=f"Противоник влучив у ваш корабель! Його хід ще раз.")

            # Перевіряємо кінець гри
            if sum(self.computer_destroyed.values()) == 10:
                self.game_over(False)
                return

            # Комп'ютер ходить ще раз
            self.root.after(1000, self.computer_turn)
        else:
            self.computer_shots[y][x] = 1  # Промах
            self.player_buttons[y][x].config(
                text=self.symbols['miss'],
                bg=self.colors['last_move']
            )
            self.computer_miss += 1
            self.player_turn = True
            self.last_computer_move = (x, y)
            self.message.config(text="Противоник промахнувся. Ваш хід.")

        self.update_counters()

    def find_best_shot(self):
        """Знайти найкращий постріл для комп'ютера"""
        # Якщо є незавершені попадання - добиваємо корабель
        if self.computer_hit_cells:
            # Якщо тільки одне попадання - стріляємо у сусідні клітинки
            if len(self.computer_hit_cells) == 1:
                x, y = self.computer_hit_cells[0]
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Тільки по прямим
                random.shuffle(directions)  # Перемішуємо напрямки для випадковості

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.size and 0 <= ny < self.size:
                        if self.computer_shots[ny][nx] == 0:  # Ще не стріляли
                            return nx, ny

            # Якщо кілька попадань, визначаємо напрямок корабля
            else:
                # Сортуємо попадання, щоб визначити напрямок
                sorted_hits = sorted(self.computer_hit_cells)

                # Перевіряємо горизонтальний напрямок
                if all(cell[1] == sorted_hits[0][1] for cell in sorted_hits):
                    # Стріляємо в крайні клітинки
                    first_x = sorted_hits[0][0]
                    last_x = sorted_hits[-1][0]

                    # Перевіряємо зліва
                    if first_x > 0 and self.computer_shots[sorted_hits[0][1]][first_x - 1] == 0:
                        return first_x - 1, sorted_hits[0][1]
                    # Перевіряємо справа
                    if last_x < self.size - 1 and self.computer_shots[sorted_hits[0][1]][last_x + 1] == 0:
                        return last_x + 1, sorted_hits[0][1]

                # Перевіряємо вертикальний напрямок
                elif all(cell[0] == sorted_hits[0][0] for cell in sorted_hits):
                    # Стріляємо в крайні клітинки
                    first_y = sorted_hits[0][1]
                    last_y = sorted_hits[-1][1]

                    # Перевіряємо зверху
                    if first_y > 0 and self.computer_shots[first_y - 1][sorted_hits[0][0]] == 0:
                        return sorted_hits[0][0], first_y - 1
                    # Перевіряємо знизу
                    if last_y < self.size - 1 and self.computer_shots[last_y + 1][sorted_hits[0][0]] == 0:
                        return sorted_hits[0][0], last_y + 1

        # Якщо поранених кораблів немає, використовуємо ймовірнісний алгоритм
        best_score = -1
        best_cells = []

        for y in range(self.size):
            for x in range(self.size):
                if self.computer_shots[y][x] == 0:  # Тільки в нестріляні клітинки
                    score = 0

                    # Перевіряємо всі можливі кораблі, які можуть проходити через цю клітинку
                    for size in [4, 3, 2, 1]:
                        # Горизонтальні кораблі
                        for i in range(size):
                            nx = x - i
                            if nx >= 0 and nx + size <= self.size:
                                valid = True
                                for j in range(size):
                                    if self.computer_shots[y][nx + j] == 1:  # Якщо там промах - корабель не може бути
                                        valid = False
                                        break
                                if valid:
                                    score += 1

                        # Вертикальні кораблі
                        for i in range(size):
                            ny = y - i
                            if ny >= 0 and ny + size <= self.size:
                                valid = True
                                for j in range(size):
                                    if self.computer_shots[ny + j][x] == 1:
                                        valid = False
                                        break
                                if valid:
                                    score += 1

                    # Додаємо випадковий елемент для різноманітності
                    score += random.random() * 0.1

                    if score > best_score:
                        best_score = score
                        best_cells = [(x, y)]
                    elif score == best_score:
                        best_cells.append((x, y))

        # Вибираємо випадкову клітинку з найкращих
        if best_cells:
            return random.choice(best_cells)

        # Якщо все інше не спрацювало, стріляємо випадково
        empty_cells = [(x, y) for y in range(self.size) for x in range(self.size)
                       if self.computer_shots[y][x] == 0]
        if empty_cells:
            return random.choice(empty_cells)

        return 0, 0  # На всяк випадок

    def game_over(self, player_won):
        """Завершение игры с обработкой всех возможных ошибок"""
        try:
            self.playing = False

            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60

            if not player_won:
                for ship in self.computer_ships:
                    for x, y in ship:
                        if 0 <= x < self.size and 0 <= y < self.size:
                            if self.player_shots[y][x] == 0:
                                if (y < len(self.computer_buttons) and
                                        x < len(self.computer_buttons[y]) and
                                        self.computer_buttons[y][x] is not None):
                                    self.computer_buttons[y][x].config(
                                        text=self.symbols['ship'],
                                        bg=self.colors['ship']
                                    )

            if player_won:
                for ship in self.computer_ships:
                    size = len(ship)
                    if not all(0 <= cx < self.size and 0 <= cy < self.size and
                               self.player_shots[cy][cx] == 2 for (cx, cy) in ship):
                        self.player_destroyed[size] += 1

                        for i, (x, y) in enumerate(ship):
                            if 0 <= x < self.size and 0 <= y < self.size:
                                is_last = (i == len(ship) - 1)
                                self.root.after(300 * i, partial(
                                    self.animate_ship_destruction,
                                    x, y,
                                    self.computer_buttons,
                                    is_last
                                ))
                        break
            else:
                for ship in self.player_ships:
                    size = len(ship)
                    if not all(0 <= cx < self.size and 0 <= cy < self.size and
                               self.computer_shots[cy][cx] == 2 for (cx, cy) in ship):
                        self.computer_destroyed[size] += 1

                        for i, (x, y) in enumerate(ship):
                            if 0 <= x < self.size and 0 <= y < self.size:
                                is_last = (i == len(ship) - 1)
                                self.root.after(300 * i, partial(
                                    self.animate_ship_destruction,
                                    x, y,
                                    self.player_buttons,
                                    is_last
                                ))
                        break

            self.update_counters()

            if player_won:
                message = f"ВИ ПЕРЕМОГЛИ! ЧАС: {minutes:02d}:{seconds:02d}"
                color = "#4CAF50"
            else:
                message = f"ВИ ПРОГРАЛИ! ЧАС: {minutes:02d}:{seconds:02d}"
                color = "#F44336"

            if hasattr(self, 'message') and self.message.winfo_exists():
                if player_won:
                    self.animate_victory_message(message, color)
                else:
                    self.animate_defeat_message(message, color)

        except Exception as e:
            print(f"Ошибка в game_over: {e}")
            if hasattr(self, 'message') and self.message.winfo_exists():
                self.message.config(text="Игра завершена!", fg="#FF0000")

    def animate_victory_message(self, message, color):
        """Анімація повідомлення про перемогу"""
        sizes = [24, 28, 32, 36, 32, 28, 24, 28, 32, 36]
        colors = [self.lighter_color(color, i * 10) for i in range(5)]

        def animate_step(step):
            if step < len(sizes):
                self.message.config(
                    text=message,
                    font=("Arial", sizes[step], "bold"),
                    fg=colors[step % len(colors)]
                )
                self.root.after(150, animate_step, step + 1)
            else:
                self.message.config(
                    text=message,
                    font=("Arial", 24, "bold"),
                    fg=color
                )

        animate_step(0)

    def animate_defeat_message(self, message, color):
        """Анімація повідомлення про поразку"""
        from math import sin

        def animate_step(step):
            if step < 20:
                # Ефект "тремтіння"
                offset_x = int(5 * sin(step * 0.5))
                offset_y = int(2 * sin(step * 0.7))

                self.message.config(
                    text=message,
                    font=("Arial", 24, "bold"),
                    fg=color,
                    padx=offset_x,
                    pady=offset_y
                )
                self.root.after(100, animate_step, step + 1)
            else:
                self.message.config(
                    text=message,
                    font=("Arial", 24, "bold"),
                    fg=color,
                    padx=0,
                    pady=0
                )

        animate_step(0)

    def animate_ship_destruction(self, x, y, board, is_last=False):
        """Анімація знищення корабля"""
        if is_last:
            # Для останнього попадання - особлива анімація
            colors = [self.colors['last_move'], '#FF8C00', '#FF4500', self.colors['dead']]
        else:
            # Для інших частин корабля
            colors = [self.colors['hit'], '#FF6347', '#FF4500', self.colors['dead']]

        # Початкові параметри
        size = 16
        steps = 10

        def animate_step(step):
            if step < steps:
                # Зміна кольору
                color_idx = min(int(step / (steps / len(colors))), len(colors) - 1)
                color = colors[color_idx]

                # Зміна розміру (пульсація)
                current_size = size + (2 if step % 2 == 0 else -2)

                # Оновлюємо кнопку
                board[y][x].config(
                    text=self.symbols['dead'],
                    bg=color,
                    font=('Arial', current_size, 'bold')
                )

                # Наступний крок
                self.root.after(100, animate_step, step + 1)
            else:
                # Фінальний стан
                board[y][x].config(
                    text=self.symbols['dead'],
                    bg=self.colors['dead'] if not is_last else self.colors['last_move'],
                    font=('Arial', size)
                )

        animate_step(0)

    # ==================== ДОПОМІЖНІ ФУНКЦІЇ ====================

    def clear(self):
        """Очистити вікно"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def handle_keypress(self, event):
        """Обробник натискань клавіш"""
        if not self.placing_ships:
            return

        key = event.keysym.lower()

        if key == 'q' or (key in ('control_l', 'control_r') or (event.state & 0x4)):  # Q або будь-який Ctrl
            if hasattr(self, 'selected_ship') and self.selected_ship:
                self.rotate_selected_ship()
        elif key in ('left', 'a'):
            self.move_ship(-1, 0)
        elif key in ('right', 'd'):
            self.move_ship(1, 0)
        elif key in ('up', 'w'):
            self.move_ship(0, -1)
        elif key in ('down', 's'):
            self.move_ship(0, 1)

    def on_button_enter(self, btn, event=None):
        btn.config(bg=self.lighter_color(btn.cget("bg")))


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.bind('<Key>', game.handle_keypress)
    root.mainloop()