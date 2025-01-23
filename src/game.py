import pygame
import sys
import random

pygame.init()

WIDTH = 600
HEIGHT = 600
LINE_WIDTH = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("крестики-нолики")

font = pygame.font.SysFont(None, 60)

board = [[0 for _ in range(3)] for _ in range(3)]

# текущий игрок (1 – человек (X), 2 – компьютер (O))
current_player = 1

CELL_SIZE = WIDTH // 3

game_over = False
winner = None

def draw_board():
    """функция отрисовки игрового поля и уже сделанных ходов."""
    screen.fill(WHITE)

    pygame.draw.line(screen, BLACK, (0, CELL_SIZE), (WIDTH, CELL_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, BLACK, (0, 2 * CELL_SIZE), (WIDTH, 2 * CELL_SIZE), LINE_WIDTH)

    pygame.draw.line(screen, BLACK, (CELL_SIZE, 0), (CELL_SIZE, HEIGHT), LINE_WIDTH)
    pygame.draw.line(screen, BLACK, (2 * CELL_SIZE, 0), (2 * CELL_SIZE, HEIGHT), LINE_WIDTH)

    for row in range(3):
        for col in range(3):
            if board[row][col] == 1:
                x = col * CELL_SIZE
                y = row * CELL_SIZE

                pygame.draw.line(screen, RED,
                                 (x + 20, y + 20),
                                 (x + CELL_SIZE - 20, y + CELL_SIZE - 20),
                                 LINE_WIDTH)
                pygame.draw.line(screen, RED,
                                 (x + 20, y + CELL_SIZE - 20),
                                 (x + CELL_SIZE - 20, y + 20),
                                 LINE_WIDTH)
            elif board[row][col] == 2:
                x = col * CELL_SIZE + CELL_SIZE // 2
                y = row * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(screen, BLUE, (x, y), CELL_SIZE // 2 - 20, LINE_WIDTH)

def check_winner():
    """проверяем, есть ли победитель, и возвращаем 1 (X) / 2 (O) или none, если победителя пока нет.
       если ничья, возвращаем 'draw'."""
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != 0:
            return board[row][0]

    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != 0:
            return board[0][col]

    if board[0][0] == board[1][1] == board[2][2] != 0:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != 0:
        return board[0][2]

    for row in range(3):
        for col in range(3):
            if board[row][col] == 0:
                return None

    return 'draw'

def computer_move():
    """
        1) если где-то можно выиграть следующим ходом – делаем.
        2) если игрок может выиграть следующим ходом – блокируем.
        3) иначе ходим в случайную свободную клетку.
    """
    move = find_winning_move(2)
    if move:
        row, col = move
        board[row][col] = 2
        return

    move = find_winning_move(1)
    if move:
        row, col = move
        board[row][col] = 2
        return

    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == 0]
    if empty_cells:
        row, col = random.choice(empty_cells)
        board[row][col] = 2

def find_winning_move(player):
    """
    проверяем, есть ли у игрока (1 или 2) комбинация 2 в ряд
    с пустой третьей ячейкой, чтобы закончить игру или заблокировать.
    возвращаем координаты хода (row, col) или none.
    """
    for row in range(3):
        if board[row].count(player) == 2 and board[row].count(0) == 1:
            col = board[row].index(0)
            return (row, col)

    for col in range(3):
        column = [board[row][col] for row in range(3)]
        if column.count(player) == 2 and column.count(0) == 1:
            row = column.index(0)
            return (row, col)

    diag1 = [board[i][i] for i in range(3)]
    diag2 = [board[i][2 - i] for i in range(3)]

    if diag1.count(player) == 2 and diag1.count(0) == 1:
        row = diag1.index(0)
        return (row, row)

    if diag2.count(player) == 2 and diag2.count(0) == 1:
        row = diag2.index(0)
        col = 2 - row
        return (row, col)

    return None

def draw_result(text):
    """отрисовка сообщения о результате в центре экрана."""
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_over and event.type == pygame.MOUSEBUTTONDOWN and current_player == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            clicked_row = mouse_y // CELL_SIZE
            clicked_col = mouse_x // CELL_SIZE

            if board[clicked_row][clicked_col] == 0:
                board[clicked_row][clicked_col] = 1
                result = check_winner()
                if result is not None:
                    game_over = True
                    winner = result
                else:
                    current_player = 2

    if not game_over and current_player == 2:
        computer_move()
        result = check_winner()
        if result is not None:
            game_over = True
            winner = result
        else:
            current_player = 1

    draw_board()

    if game_over:
        if winner == 'draw':
            draw_result("ничья!")
        elif winner == 1:
            draw_result("вы выиграли!")
        elif winner == 2:
            draw_result("компьютер выиграл!")

    pygame.display.update()
