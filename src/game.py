import pygame
import sys
import math
import random
import json
import os
import time

pygame.init()

# ----------------------------------------
# НАСТРОЙКИ ОКНА
# ----------------------------------------
WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // 3
LINE_WIDTH = 5

# ----------------------------------------
# ОТРИСОВКА / ЦВЕТА / ШРИФТЫ
# ----------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 200, 0)
GRAY  = (200, 200, 200)
ORANGE = (255, 150, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
PINK = (255, 0, 255)
BROWN = (150, 75, 0)
MAGENTA = (255, 0, 255)
LIGHT_BLUE = (0, 0, 255)
LIGHT_GREEN = (0, 255, 0)
DARK_CYAN = (0, 153, 153)
RASPBERRY = (179, 0, 89)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Крестики-нолики (Расширенная версия)")
        
menu_font = pygame.font.Font("joystix_monospace.ttf", 30)   # шрифт для меню
game_font = pygame.font.SysFont(None, 60)   # шрифт для результатов
small_font = pygame.font.SysFont(None, 30)  # шрифт для мелких надписей

clock = pygame.time.Clock()






def render_text_with_outline(text, font, text_color, outline_color, outline_width):
    """
    Рендер текста с обводкой.
    
    :param text: Текст для отображения.
    :param font: Объект шрифта Pygame.
    :param text_color: Цвет основного текста.
    :param outline_color: Цвет обводки.
    :param outline_width: Толщина обводки.
    :return: Поверхность с текстом с обводкой.
    """
    text_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)
    outline_size = outline_width

    final_surface = pygame.Surface(
        (text_surface.get_width() + outline_size * 2, text_surface.get_height() + outline_size * 2),
        pygame.SRCALPHA
    )

    for dx in range(-outline_size, outline_size + 1):
        for dy in range(-outline_size, outline_size + 1):
            if dx != 0 or dy != 0:
                final_surface.blit(outline_surface, (dx + outline_size, dy + outline_size))

    final_surface.blit(text_surface, (outline_size, outline_size))

    return final_surface



# ----------------------------------------
# ЗАГРУЗКА ИЗОБРАЖЕНИЙ (ШАБЛОНЫ)
# ----------------------------------------
try:
    bg_menu = pygame.image.load("start_backgound.png")
    bg_menu = pygame.transform.scale(bg_menu, (WIDTH, HEIGHT))
except:
    bg_menu = None

try:
    bg_ai_menu = pygame.image.load("computer_mode_background.png")
    bg_ai_menu = pygame.transform.scale(bg_ai_menu, (WIDTH, HEIGHT))
except:
    bg_ai_menu = None

try:
    bg_game = pygame.image.load("game_field.png")
    bg_game = pygame.transform.scale(bg_game, (WIDTH, HEIGHT))
except:
    bg_game = None

try:
    x_skin = pygame.image.load("x_skin.png")
    x_skin = pygame.transform.scale(x_skin, (CELL_SIZE - 40, CELL_SIZE - 40))
except:
    x_skin = None

try:
    o_skin = pygame.image.load("o_skin.png")
    o_skin = pygame.transform.scale(o_skin, (CELL_SIZE - 40, CELL_SIZE - 40))
except:
    o_skin = None

# ----------------------------------------
# ЗАГРУЗКА ЗВУКОВ/МУЗЫКИ (ШАБЛОНЫ)
# ----------------------------------------
pygame.mixer.init()
try:
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.play(-1)  # зациклить
    pygame.mixer.music.set_volume(0.2)
except:
    print("Фоновая музыка не найдена. Игра продолжается без музыки.")

try:
    move_sound = pygame.mixer.Sound("move.wav")
    move_sound.set_volume(0.5)
except:
    move_sound = None

try:
    win_sound = pygame.mixer.Sound("win.wav")
    win_sound.set_volume(0.7)
except:
    win_sound = None

# ----------------------------------------
# СЧЁТ и СТАТИСТИКА (JSON)
# ----------------------------------------
SCOREBOARD_FILE = "scoreboard.json"

# Шаблон структуры счёта / статистики
scoreboard_template = {
    "two_players": {
        "games_played": 0,
        "player1_wins": 0,
        "player2_wins": 0,
        "draws": 0,
        "best_streak_p1": 0,
        "best_streak_p2": 0,
        "current_streak_p1": 0,
        "current_streak_p2": 0
    },
    "vs_ai": {
        "games_played": 0,
        "human_wins": 0,
        "computer_wins": 0,
        "draws": 0,
        "best_streak_human": 0,
        "best_streak_comp": 0,
        "current_streak_human": 0,
        "current_streak_comp": 0
    }
}

def load_scoreboard():
    if os.path.exists(SCOREBOARD_FILE):
        try:
            with open(SCOREBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except:
            print("Ошибка чтения scoreboard.json. Используем счёт по умолчанию.")
            return scoreboard_template
    else:
        return scoreboard_template

def save_scoreboard(data):
    with open(SCOREBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

scoreboard = load_scoreboard()

# ----------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ СТАТИСТИКИ
# ----------------------------------------
def update_win_streak(mode, winner_side):
    """Обновляем винстрики и общее кол-во игр, побед, ничьих."""
    # mode: "two_players" или "vs_ai"
    # winner_side: 1, 2, 'draw', 'human', 'computer' (зависит от режима)
    data = scoreboard[mode]
    data["games_played"] += 1

    if mode == "two_players":
        # winner_side = 1, 2 или 'draw'
        if winner_side == 1:
            data["player1_wins"] += 1
            data["current_streak_p1"] += 1
            data["current_streak_p2"] = 0
            if data["current_streak_p1"] > data["best_streak_p1"]:
                data["best_streak_p1"] = data["current_streak_p1"]
        elif winner_side == 2:
            data["player2_wins"] += 1
            data["current_streak_p2"] += 1
            data["current_streak_p1"] = 0
            if data["current_streak_p2"] > data["best_streak_p2"]:
                data["best_streak_p2"] = data["current_streak_p2"]
        elif winner_side == 'draw':
            data["draws"] += 1
            # ничья обнуляет обе серии
            data["current_streak_p1"] = 0
            data["current_streak_p2"] = 0

    else:
        # vs_ai
        # winner_side = 'human', 'computer' или 'draw'
        if winner_side == 'human':
            data["human_wins"] += 1
            data["current_streak_human"] += 1
            data["current_streak_comp"] = 0
            if data["current_streak_human"] > data["best_streak_human"]:
                data["best_streak_human"] = data["current_streak_human"]
        elif winner_side == 'computer':
            data["computer_wins"] += 1
            data["current_streak_comp"] += 1
            data["current_streak_human"] = 0
            if data["current_streak_comp"] > data["best_streak_comp"]:
                data["best_streak_comp"] = data["current_streak_comp"]
        elif winner_side == 'draw':
            data["draws"] += 1
            # ничья обнуляет обе серии
            data["current_streak_human"] = 0
            data["current_streak_comp"] = 0

    save_scoreboard(scoreboard)

# ----------------------------------------
# ИГРОВОЕ ПОЛЕ
# ----------------------------------------
board = [[0]*3 for _ in range(3)]  # 0=пусто, 1=X, 2=O
game_over = False
winner = None

game_mode = None
difficulty = 1.0
human_side = 1

current_player = 1

# ----------------------------------------
# АНИМАЦИЯ ВЫИГРЫШНОЙ ЛИНИИ
# ----------------------------------------
# если кто-то выиграл, вычислим start/end (в пикселях), 
# и будем рисовать "растущую" линию (progress от 0 до 1).
win_line_start = None
win_line_end = None
win_line_progress = 0.0
win_line_speed = 0.02  # скорость "озарения"

# ----------------------------------------
# СОСТОЯНИЯ ПРИЛОЖЕНИЯ
# ----------------------------------------
STATE_MENU       = "MENU"
STATE_MENU_AI    = "MENU_AI"
STATE_GAME       = "GAME"
current_state    = STATE_MENU

# ----------------------------------------
# КНОПКИ МЕНЮ (Для «клика мышью»)
# ----------------------------------------

class MenuButton:
    def __init__(self, x, y, w, h, text, callback, font, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.font = font
        self.text_color = text_color

    def draw(self, surface):
        txt_surf = self.font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
buttons_menu = []
buttons_menu_ai = []

# ----------------------------------------
# ФУНКЦИИ МЕНЮ
# ----------------------------------------
def start_two_players():
    global game_mode, current_state
    game_mode = "two_players"
    restart_game()
    current_state = STATE_GAME

def start_vs_ai():
    global current_state
    current_state = STATE_MENU_AI  # подменю

def quit_game():
    save_scoreboard(scoreboard)
    pygame.quit()
    sys.exit()

def init_main_menu_buttons():

    btn_w, btn_h = 300, 50
    x = (WIDTH - btn_w)//2
    y_start = 220
    gap = 70
    button_font = pygame.font.Font("joystix_monospace.ttf", 20)

    b1 = MenuButton(30, 160, 200, 50, "ИГРА НА ДВОИХ", start_two_players, button_font, text_color=DARK_CYAN)
    b2 = MenuButton(350, 160, 200, 50, "ИГРА ПРОТИВ ИИ", start_vs_ai, button_font, text_color=RASPBERRY)
    b3 = MenuButton(50, 510, 200, 50, "ВЫХОД", quit_game, button_font, text_color=(102, 0, 0))
    buttons_menu.extend([b1, b2, b3])

# ----------------------------------------
# ПОДМЕНЮ vs AI
# Здесь выберем сложность и сторону (X или O).
# ----------------------------------------
def set_difficulty_easy():
    global difficulty
    difficulty = 0.2
    print("Сложность: EASY")

def set_difficulty_medium():
    global difficulty
    difficulty = 0.5
    print("Сложность: MEDIUM")

def set_difficulty_hard():
    global difficulty
    difficulty = 0.8
    print("Сложность: HARD")

def set_difficulty_impossible():
    global difficulty
    difficulty = 1.0
    print("Сложность: IMPOSSIBLE")

def set_side_x():
    global human_side, game_mode, current_state
    human_side = 1
    game_mode = "vs_ai"
    restart_game()
    current_state = STATE_GAME

def set_side_o():
    global human_side, game_mode, current_state
    human_side = 2
    game_mode = "vs_ai"
    restart_game()
    current_state = STATE_GAME

def back_to_menu():
    global current_state
    current_state = STATE_MENU

def init_menu_ai_buttons():
    btn_w, btn_h = 250, 40
    x = (WIDTH - btn_w)//2
    y_start = 150
    gap = 50
    button_font = pygame.font.Font("joystix_monospace.ttf", 30)

    b_easy = MenuButton(x, y_start, btn_w, btn_h, "Easy (20%)", set_difficulty_easy, button_font, text_color=(255, 255, 255))
    b_med  = MenuButton(x, y_start + gap, btn_w, btn_h, "Medium (50%)", set_difficulty_medium, button_font, text_color=(255, 255, 255))
    b_hard = MenuButton(x, y_start + gap*2, btn_w, btn_h, "Hard (80%)", set_difficulty_hard, button_font, text_color=(255, 255, 255))
    b_imp  = MenuButton(x, y_start + gap*3, btn_w, btn_h, "Impossible (100%)", set_difficulty_impossible, button_font, text_color=(255, 255, 255))

    b_side_x = MenuButton(x, y_start + gap*5, btn_w, btn_h, "Я играю за X", set_side_x, button_font, text_color=(255, 255, 255))
    b_side_o = MenuButton(x, y_start + gap*6, btn_w, btn_h, "Я играю за O", set_side_o, button_font, text_color=(255, 255, 255))

    b_back = MenuButton(10, HEIGHT - 60, 120, 40, "< Назад", back_to_menu, button_font, text_color=(255, 255, 255))

    buttons_menu_ai.extend([b_easy, b_med, b_hard, b_imp, b_side_x, b_side_o, b_back])


# ----------------------------------------
# ИГРОВЫЕ ФУНКЦИИ
# ----------------------------------------
def restart_game():
    """Полный сброс игрового поля и флагов."""
    global board, game_over, winner, current_player
    global win_line_start, win_line_end, win_line_progress

    print("Restarting the game...")
    board = [[0]*3 for _ in range(3)]
    game_over = False
    winner = None
    win_line_start = None
    win_line_end = None
    win_line_progress = 0.0

    if game_mode == "two_players":
        current_player = 1
    else:
        # vs AI
        if human_side == 1:
            current_player = 1
        else:
            current_player = 1

def draw_board():
    """Отрисовка поля."""
    if bg_game:
        screen.blit(bg_game, (0,0))
    else:
        screen.fill(WHITE)

    # линии
    for i in range(1, 3):
        pygame.draw.line(screen, BLACK, (0, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (i*CELL_SIZE, 0), (i*CELL_SIZE, HEIGHT), LINE_WIDTH)

    # X / O
    for row in range(3):
        for col in range(3):
            cell_value = board[row][col]
            x_pix = col * CELL_SIZE
            y_pix = row * CELL_SIZE
            if cell_value == 1:  # X
                if x_skin:
                    rect = x_skin.get_rect(center=(x_pix + CELL_SIZE//2, y_pix + CELL_SIZE//2))
                    screen.blit(x_skin, rect)
                else:
                    # Рисуем крест
                    pygame.draw.line(screen, RED, (x_pix+20, y_pix+20), (x_pix+CELL_SIZE-20, y_pix+CELL_SIZE-20), LINE_WIDTH)
                    pygame.draw.line(screen, RED, (x_pix+20, y_pix+CELL_SIZE-20), (x_pix+CELL_SIZE-20, y_pix+20), LINE_WIDTH)
            elif cell_value == 2:  # O
                if o_skin:
                    rect = o_skin.get_rect(center=(x_pix + CELL_SIZE//2, y_pix + CELL_SIZE//2))
                    screen.blit(o_skin, rect)
                else:
                    pygame.draw.circle(screen, BLUE, (x_pix + CELL_SIZE//2, y_pix + CELL_SIZE//2),
                                       CELL_SIZE//2 - 20, LINE_WIDTH)

def check_winner():
    """Проверяем победителя: 1, 2, 'draw' или None."""
    # Строки
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != 0:
            return board[r][0], ("row", r)
    # Столбцы
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != 0:
            return board[0][c], ("col", c)
    # Диагонали
    if board[0][0] == board[1][1] == board[2][2] != 0:
        return board[0][0], ("diag", 1)
    if board[0][2] == board[1][1] == board[2][0] != 0:
        return board[0][2], ("diag", 2)

    # Свободные клетки?
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                return None, None
    return 'draw', None

def get_win_line_coords(win_info):
    """Возвращает (start, end) в пикселях для выигрышной линии, исходя из win_info."""
    # win_info = ("row", r) или ("col", c) или ("diag", 1/2)
    t, idx = win_info
    if t == "row":
        # Горизонтальная линия посередине строки
        y = idx * CELL_SIZE + CELL_SIZE//2
        return (0, y), (WIDTH, y)
    elif t == "col":
        # Вертикальная линия посередине столбца
        x = idx * CELL_SIZE + CELL_SIZE//2
        return (x, 0), (x, HEIGHT)
    elif t == "diag":
        if idx == 1:
            # главная диагональ
            return (0, 0), (WIDTH, HEIGHT)
        else:
            # побочная диагональ
            return (WIDTH, 0), (0, HEIGHT)

def draw_win_line():
    """Анимация "озарения" при победе."""
    if win_line_start and win_line_end and win_line_progress < 1.0:
        # Интерполируем конец
        sx, sy = win_line_start
        ex, ey = win_line_end
        cx = sx + (ex - sx) * win_line_progress
        cy = sy + (ey - sy) * win_line_progress

        pygame.draw.line(screen, GREEN, (sx, sy), (cx, cy), 10)

def evaluate_board():
    """
    Оценка для minimax:
      +1, если компьютер выигрывает
      -1, если человек выигрывает
      0, если ничья
      None, если не закончено
    """
    comp_side = 2 if human_side == 1 else 1
    res, _ = check_winner()
    if res == comp_side:
        return +1
    elif res == human_side:
        return -1
    elif res == 'draw':
        return 0
    else:
        return None

def minimax(alpha, beta, is_maximizing):
    score = evaluate_board()
    if score is not None:
        return score

    comp_side = 2 if human_side == 1 else 1
    hum_side = human_side

    if is_maximizing:  # ход компьютера
        max_eval = -math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = comp_side
                    eval_ = minimax(alpha, beta, False)
                    board[r][c] = 0
                    max_eval = max(max_eval, eval_)
                    alpha = max(alpha, eval_)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break
        return max_eval
    else:  # ход человека
        min_eval = math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = hum_side
                    eval_ = minimax(alpha, beta, True)
                    board[r][c] = 0
                    min_eval = min(min_eval, eval_)
                    beta = min(beta, eval_)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break
        return min_eval

def get_best_move():
    comp_side = 2 if human_side == 1 else 1
    best_score = -math.inf
    best_move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                board[r][c] = comp_side
                score = minimax(-math.inf, math.inf, False)
                board[r][c] = 0
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
    return best_move

def get_random_move():
    empty = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                empty.append((r, c))
    return random.choice(empty) if empty else None

def computer_move():
    if random.random() < difficulty:
        move = get_best_move()
    else:
        move = get_random_move()
    if move:
        r, c = move
        comp_side = 2 if human_side == 1 else 1
        board[r][c] = comp_side
        if move_sound:
            move_sound.play()

# ----------------------------------------
# ИНИЦИАЛИЗАЦИЯ
# ----------------------------------------
init_main_menu_buttons()
init_menu_ai_buttons()

# ----------------------------------------
# ГЛАВНЫЙ ЦИКЛ
# ----------------------------------------
while True:
    clock.tick(60)
    for event in pygame.event.get():
        print(event)
        if event.type == pygame.QUIT:
            save_scoreboard(scoreboard)
            pygame.quit()
            sys.exit()
           


        # ОБРАБОТКА СОСТОЯНИЙ
        if current_state == STATE_MENU:
            for btn in buttons_menu:
                btn.handle_event(event)

        elif current_state == STATE_MENU_AI:
            for btn in buttons_menu_ai:
                btn.handle_event(event)

        elif current_state == STATE_GAME:
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                elif event.key == pygame.K_ESCAPE:
                    current_state = STATE_MENU

            if not game_over:
                if game_mode == "two_players":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        row = my // CELL_SIZE
                        col = mx // CELL_SIZE
                        if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == 0:
                            board[row][col] = current_player
                            if move_sound:
                                move_sound.play()
                            res, wininfo = check_winner()
                            if res is not None:
                                game_over = True
                                winner = res
                                if winner != 'draw':
                                    start, end = get_win_line_coords(wininfo) if wininfo else (None, None)
                                    win_line_start = start
                                    win_line_end = end
                                    if win_sound and winner != 'draw':
                                        win_sound.play()
                                if winner == 1:
                                    update_win_streak("two_players", 1)
                                elif winner == 2:
                                    update_win_streak("two_players", 2)
                                else:
                                    update_win_streak("two_players", 'draw')
                            else:
                                current_player = 1 if current_player == 2 else 2
                else:
                    # vs AI
                    # если ход человека
                    comp_side = 2 if human_side == 1 else 1
                    if current_player == human_side:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mx, my = event.pos
                            row = my // CELL_SIZE
                            col = mx // CELL_SIZE
                            if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == 0:
                                board[row][col] = human_side
                                if move_sound:
                                    move_sound.play()
                                res, wininfo = check_winner()
                                if res is not None:
                                    game_over = True
                                    winner = res
                                    if winner != 'draw':
                                        start, end = get_win_line_coords(wininfo) if wininfo else (None, None)
                                        win_line_start = start
                                        win_line_end = end
                                        if win_sound and winner != 'draw':
                                            win_sound.play()
                                    # статистика
                                    if winner == human_side:
                                        update_win_streak("vs_ai", 'human')
                                    elif winner == comp_side:
                                        update_win_streak("vs_ai", 'computer')
                                    else:
                                        update_win_streak("vs_ai", 'draw')
                                else:
                                    current_player = comp_side

                # # Перезапуск по R
                # if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                #     restart_game()
                #     if event.type == pygame.KEYDOWN:
                #         print(f"Key pressed: {event.key}")


                # # Назад в меню по ESC
                # if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                #     current_state = STATE_MENU
                    

    # ЛОГИКА vs AI: если ход компьютера
    if current_state == STATE_GAME and not game_over and game_mode == "vs_ai":
        comp_side = 2 if human_side == 1 else 1
        if current_player == comp_side:
            computer_move()
            res, wininfo = check_winner()
            if res is not None:
                game_over = True
                winner = res
                if winner != 'draw':
                    start, end = get_win_line_coords(wininfo) if wininfo else (None, None)
                    win_line_start = start
                    win_line_end = end
                    if win_sound and winner != 'draw':
                        win_sound.play()
                # статистика
                if winner == comp_side:
                    update_win_streak("vs_ai", 'computer')
                elif winner == human_side:
                    update_win_streak("vs_ai", 'human')
                else:
                    update_win_streak("vs_ai", 'draw')
            else:
                current_player = human_side

    # ----------------------------------------
    # ОТРИСОВКА
    # ----------------------------------------
    if current_state == STATE_MENU:
        if bg_menu:
            screen.blit(bg_menu, (0, 0))
        else:
            screen.fill(WHITE)
        title_surf = render_text_with_outline("КРЕСТИКИ-НОЛИКИ", menu_font, (255, 230, 204), (102, 0, 51), 2)
        
        
        title_rect = title_surf.get_rect(center=(WIDTH//2, 40))
        screen.blit(title_surf, title_rect)

    # Отрисовка кнопок
        for btn in buttons_menu:
            btn.draw(screen)

            tp = scoreboard["two_players"]
            va = scoreboard["vs_ai"]
            stats_text = (f"2P: сыграно {tp['games_played']}\n P1:{tp['player1_wins']} P2:{tp['player2_wins']} D:{tp['draws']}\n"
                  f"vsAI: сыграно {va['games_played']}\n Human:{va['human_wins']} PC:{va['computer_wins']} D:{va['draws']}")
            lines = stats_text.split("\n")
            y = 350
            for line in lines:
                s = small_font.render(line, True, BLACK)
                r = s.get_rect(center=(WIDTH//2, y))
                screen.blit(s, r)
                y += 30

    elif current_state == STATE_MENU_AI:
        if bg_ai_menu:
            screen.blit(bg_ai_menu, (0, 0))
        else:
            screen.fill(WHITE)

        # Заголовок
        sub_title = menu_font.render("РЕЖИМ: Против компьютера", True, BLACK)
        sub_rect = sub_title.get_rect(center=(WIDTH//2, 80))
        screen.blit(sub_title, sub_rect)

        # Инструкция
        info_text = "Сначала выберите сложность, затем сторону (X / O)."
        info_surf = small_font.render(info_text, True, BLACK)
        info_rect = info_surf.get_rect(center=(WIDTH//2, 120))
        screen.blit(info_surf, info_rect)

        # Кнопки
        for btn in buttons_menu_ai:
            btn.draw(screen)

    elif current_state == STATE_GAME:
        draw_board()

        # Если есть анимация выигрышной линии
        if game_over and winner != 'draw' and win_line_start and win_line_end and win_line_progress < 1.0:
            win_line_progress += win_line_speed
            if win_line_progress > 1.0:
                win_line_progress = 1.0
            draw_win_line()
        else:
            if game_over and winner != 'draw' and win_line_start and win_line_end:
                pygame.draw.line(screen, GREEN, win_line_start, win_line_end, 10)

        if game_over:
            if winner == 'draw':
                msg = "Ничья! (R - заново, ESC - меню)"
            elif winner == 1:
                msg = "Победил X! (R - заново, ESC - меню)"
            elif winner == 2:
                msg = "Победил O! (R - заново, ESC - меню)"

            msg_surf = game_font.render(msg, True, BLACK)
            msg_rect = msg_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(msg_surf, msg_rect)

    pygame.display.update()
