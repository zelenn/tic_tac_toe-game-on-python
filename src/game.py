import pygame
import sys
import math
import random
import json
import os

pygame.init()

# ---------------- НАСТРОЙКИ ЭКРАНА ----------------
WIDTH, HEIGHT = 600, 600
CELL_SIZE = WIDTH // 3
LINE_WIDTH = 5

# ---------------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ----------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Крестики-нолики - Меню, Сложность, Счёт")
font = pygame.font.SysFont(None, 40)
game_font = pygame.font.SysFont(None, 60)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

# ---------------- СЧЁТ (ЗАГРУЗКА / СОХРАНЕНИЕ) ----------------
# для хранения результатов используем JSON-файл
SCOREBOARD_FILE = "scoreboard.json"

# cтруктура, где:
#   "player_wins" – победы человека в режиме "vs компьютер"
#   "computer_wins" – победы компьютера
#   "player1_wins" – победы первого игрока в режиме "2 игрока"
#   "player2_wins" – победы второго игрока
#   "draws" – ничьи (общие, можно вести отдельно для двух режимов, если хотите)
scoreboard = {
    "player_wins": 0,
    "computer_wins": 0,
    "player1_wins": 0,
    "player2_wins": 0,
    "draws": 0
}

def load_scoreboard():
    if os.path.exists(SCOREBOARD_FILE):
        try:
            with open(SCOREBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except:
            print("Ошибка чтения scoreboard.json. Используем счёт по умолчанию.")
            return scoreboard
    else:
        print("Файл scoreboard.json не найден. Будет создан при сохранении.")
        return scoreboard

def save_scoreboard(data):
    with open(SCOREBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Грузим счёт при старте
scoreboard = load_scoreboard()


# ---------------- ЛОГИКА ИГРЫ ----------------
board = [[0]*3 for _ in range(3)]  # 0 = пусто, 1 = X, 2 = O
game_over = False
winner = None

game_mode = None      # "2players" или "vs_ai"
difficulty = 1.0      # 0.0 - 1.0 (вероятность, с которой ИИ ходит идеально)
human_side = 1        # Если игра против ИИ: 1 (X) или 2 (O)

current_player = 1

# ---------------- СОСТОЯНИЯ ПРИЛОЖЕНИЯ ----------------
STATE_MENU = "MENU"
STATE_GAME = "GAME"
STATE_END  = "END"
current_state = STATE_MENU  # начинаем с меню

# ---------------- ФУНКЦИИ ИГРОВОЙ ЛОГИКИ ----------------
def restart_game():
    """Полный сброс игрового поля и флагов."""
    global board, game_over, winner, current_player
    board = [[0]*3 for _ in range(3)]
    game_over = False
    winner = None
    # определяем, кто ходит первым, в зависимости от выбора X/O и режима
    if game_mode == "vs_ai":
        # если человек выбрал играть X (human_side=1) – он ходит первым
        # если человек выбрал O (human_side=2) – первым ходит компьютер (X=1).
        current_player = 1 if human_side == 1 else 1  # компьютер = 1 (X), если human_side=2
        # но если человек X, тогда current_player=1 (то есть человек).
        # для упрощения логики сделаем так:  
        # - если human_side==1 (человек = X), то current_player=1
        # - если human_side==2 (человек = O), то current_player=1 (т.е. X=компьютер) 
        #   и компьютер сразу будет ходить.
        if human_side == 1:
            current_player = 1  # человек первым
        else:
            current_player = 1  # компьютер (X) первым, человек (O) вторым
    else:
        # в режиме 2 игрока, начинаем всегда с X (1)
        current_player = 1

def draw_board():
    """Отрисовка игрового поля."""
    screen.fill(WHITE)

    # линии
    for i in range(1, 3):
        # горизонтальные
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), LINE_WIDTH)
        # вертикальные
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), LINE_WIDTH)

    # X / O
    for row in range(3):
        for col in range(3):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            if board[row][col] == 1:  # X
                pygame.draw.line(screen, RED, (x+20, y+20), (x+CELL_SIZE-20, y+CELL_SIZE-20), LINE_WIDTH)
                pygame.draw.line(screen, RED, (x+20, y+CELL_SIZE-20), (x+CELL_SIZE-20, y+20), LINE_WIDTH)
            elif board[row][col] == 2:  # O
                pygame.draw.circle(screen, BLUE, (x + CELL_SIZE//2, y + CELL_SIZE//2), CELL_SIZE//2 - 20, LINE_WIDTH)

def check_winner():
    """Проверяем победу: 1 (X) или 2 (O) или 'draw' или None."""
    # строки
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != 0:
            return board[row][0]
    # столбцы
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != 0:
            return board[0][col]
    # диагонали
    if board[0][0] == board[1][1] == board[2][2] != 0:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != 0:
        return board[0][2]

    # свободные клетки?
    for row in range(3):
        for col in range(3):
            if board[row][col] == 0:
                return None

    return 'draw'

def evaluate_board():
    """
    Оценка для minimax:
      +1, если выиграл компьютер (O или X – смотрим, кто есть компьютер)
      -1, если выиграл человек
      0, если ничья
      None, если игра не окончена
    """
    # определяем, кто есть компьютер: если human_side=1 (человек=X), значит компьютер=2 (O).
    # если human_side=2 (человек=O), компьютер=1 (X).
    comp_side = 2 if human_side == 1 else 1

    res = check_winner()
    if res == comp_side:
        return +1
    elif res == human_side:
        return -1
    elif res == 'draw':
        return 0
    else:
        return None  # игра ещё не окончена

def minimax(alpha, beta, is_maximizing):
    """Minimax с альфа-бета отсечением."""
    score = evaluate_board()
    if score is not None:
        return score

    comp_side = 2 if human_side == 1 else 1
    human = human_side

    if is_maximizing:
        # ход компьютера
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
    else:
        # ход человека
        min_eval = math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == 0:
                    board[r][c] = human
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
    """Возвращает (row, col) лучшего хода для компьютера (максимизируем оценку)."""
    best_score = -math.inf
    best_move = None
    comp_side = 2 if human_side == 1 else 1

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
    """Возвращает случайный ход (r, c) из свободных ячеек."""
    empty = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == 0:
                empty.append((r, c))
    return random.choice(empty) if empty else None

def computer_move():
    """Ход компьютера. С вероятностью `difficulty` – лучший ход, иначе случайный."""
    # если diff=1.0 – всегда лучший ход, если diff=0 – всегда случайный.
    if random.random() < difficulty:
        move = get_best_move()
    else:
        move = get_random_move()
    if move:
        r, c = move
        comp_side = 2 if human_side == 1 else 1
        board[r][c] = comp_side

# ---------------- МЕНЮ ----------------
# Для упрощения: будем рисовать текст на экране и ждать нажатия клавиш.

def draw_menu():
    screen.fill(WHITE)

    title_text = "КРЕСТИКИ-НОЛИКИ"
    t_surf = font.render(title_text, True, BLACK)
    t_rect = t_surf.get_rect(center=(WIDTH//2, 70))
    screen.blit(t_surf, t_rect)

    mode_text1 = "1 - Игра на двоих за одним ПК"
    mode_text2 = "2 - Игра против компьютера"
    m_surf1 = font.render(mode_text1, True, BLACK)
    m_rect1 = m_surf1.get_rect(center=(WIDTH//2, 150))
    screen.blit(m_surf1, m_rect1)

    m_surf2 = font.render(mode_text2, True, BLACK)
    m_rect2 = m_surf2.get_rect(center=(WIDTH//2, 200))
    screen.blit(m_surf2, m_rect2)

    sc_text = f"СЧЁТ: P1={scoreboard['player1_wins']}, P2={scoreboard['player2_wins']}, " \
              f"User={scoreboard['player_wins']}, PC={scoreboard['computer_wins']}, Draws={scoreboard['draws']}"
    sc_surf = font.render(sc_text, True, BLACK)
    sc_rect = sc_surf.get_rect(center=(WIDTH//2, 300))
    screen.blit(sc_surf, sc_rect)

def draw_menu_difficulty():
    screen.fill(WHITE)

    text1 = "Выберите сложность: "
    t_surf1 = font.render(text1, True, BLACK)
    t_rect1 = t_surf1.get_rect(center=(WIDTH//2, 100))
    screen.blit(t_surf1, t_rect1)

    text2 = "E - Простая, M - Средняя, H - Трудная, I - Невозможная"
    t_surf2 = font.render(text2, True, BLACK)
    t_rect2 = t_surf2.get_rect(center=(WIDTH//2, 150))
    screen.blit(t_surf2, t_rect2)

    text_side = "Выберите, хотите играть за X или O (нажмите X / O)"
    t_side_surf = font.render(text_side, True, BLACK)
    t_side_rect = t_side_surf.get_rect(center=(WIDTH//2, 220))
    screen.blit(t_side_surf, t_side_rect)

def difficulty_value_from_key(key):
    """Возвращаем float (0..1) по символу сложности."""
    if key == pygame.K_e:  # Easy
        return 0.2
    elif key == pygame.K_m:  # Medium
        return 0.5
    elif key == pygame.K_h:  # Hard
        return 0.8
    elif key == pygame.K_i:  # Impossible
        return 1.0
    return 1.0

def draw_result(text):
    """Вывести результат игры по центру."""
    surf = game_font.render(text, True, BLACK)
    rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(surf, rect)

# ---------------- ГЛАВНЫЙ ЦИКЛ ----------------
clock = pygame.time.Clock()

choosing_difficulty = False  # когда выбрали vs_ai, нужно уточнить сложность и сторону

while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_scoreboard(scoreboard)
            pygame.quit()
            sys.exit()

        if current_state == STATE_MENU:
            if not choosing_difficulty:
                # главное меню
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        # режим двух игроков
                        game_mode = "2players"
                        restart_game()
                        current_state = STATE_GAME
                    elif event.key == pygame.K_2:
                        # режим vs AI -> надо уточнить сложность
                        choosing_difficulty = True
            else:
                # выбираем сложность и сторону (vs_ai)
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_e, pygame.K_m, pygame.K_h, pygame.K_i]:
                        difficulty = difficulty_value_from_key(event.key)
                        # ждём выбор X/O
                    elif event.key == pygame.K_x:
                        human_side = 1  # человек = X
                        game_mode = "vs_ai"
                        restart_game()
                        current_state = STATE_GAME
                    elif event.key == pygame.K_o:
                        human_side = 2  # человек = O
                        game_mode = "vs_ai"
                        restart_game()
                        current_state = STATE_GAME

        elif current_state == STATE_GAME:
            if not game_over:
                if game_mode == "2players":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        row = y // CELL_SIZE
                        col = x // CELL_SIZE
                        if board[row][col] == 0:
                            board[row][col] = current_player
                            result = check_winner()
                            if result is not None:
                                game_over = True
                                winner = result
                            else:
                                current_player = 1 if current_player == 2 else 2

                else:
                    # определим, кто компьютер, кто человек
                    comp_side = 2 if human_side == 1 else 1
                    if current_player == human_side:
                        # ход человека
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            x, y = pygame.mouse.get_pos()
                            row = y // CELL_SIZE
                            col = x // CELL_SIZE
                            if board[row][col] == 0:
                                board[row][col] = human_side
                                result = check_winner()
                                if result is not None:
                                    game_over = True
                                    winner = result
                                else:
                                    current_player = comp_side
                    # ход компьютера в основном цикле – ниже (вне event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    restart_game()
                elif event.key == pygame.K_ESCAPE:
                    current_state = STATE_MENU
                    choosing_difficulty = False

        elif current_state == STATE_END:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                    current_state = STATE_GAME
                elif event.key == pygame.K_ESCAPE:
                    current_state = STATE_MENU
                    choosing_difficulty = False
    if current_state == STATE_GAME and not game_over:
        # если режим vs_ai и ход компьютера
        if game_mode == "vs_ai":
            comp_side = 2 if human_side == 1 else 1
            if current_player == comp_side:
                computer_move()
                result = check_winner()
                if result is not None:
                    game_over = True
                    winner = result
                else:
                    current_player = human_side

    # проверяем, если игра завершилась, переводим в STATE_END (или остаёмся в GAME и ждём R)
    if current_state == STATE_GAME and game_over:
        # ставим winner
        # обновляем scoreboard
        if winner == 1:
            # X победил
            if game_mode == "2players":
                scoreboard["player1_wins"] += 1
            else:
                # если X = computer_side?
                if human_side == 1:
                    scoreboard["player_wins"] += 1
                else:
                    scoreboard["computer_wins"] += 1
        elif winner == 2:
            # O победил
            if game_mode == "2players":
                scoreboard["player2_wins"] += 1
            else:
                # если O = computer_side?
                if human_side == 2:
                    scoreboard["player_wins"] += 1
                else:
                    scoreboard["computer_wins"] += 1
        elif winner == 'draw':
            scoreboard["draws"] += 1

        save_scoreboard(scoreboard)
        pass

    # ---------------- ОТРИСОВКА ----------------
    screen.fill(WHITE)

    if current_state == STATE_MENU:
        if not choosing_difficulty:
            draw_menu()
        else:
            draw_menu_difficulty()
    elif current_state == STATE_GAME:
        draw_board()
        if game_over:
            if winner == 'draw':
                draw_result("Ничья! (Нажмите R для новой игры или ESC - меню)")
            else:
                if winner == 1:
                    draw_result("X победил! (R - новая игра, ESC - меню)")
                elif winner == 2:
                    draw_result("O победил! (R - новая игра, ESC - меню)")
    elif current_state == STATE_END:
        if winner == 'draw':
            draw_result("Ничья! (Нажмите R или ESC)")
        else:
            if winner == 1:
                draw_result("X победил! (R или ESC)")
            else:
                draw_result("O победил! (R или ESC)")

    pygame.display.update()
