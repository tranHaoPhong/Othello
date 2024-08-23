import pygame
import sys
import copy
import random

# Define constants
WIDTH = 600
HEIGHT = 650
ROWS = 8
COLS = 8
SQUARE_SIZE = WIDTH // COLS

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
GRAY = (169, 169, 169)
RED = (255, 0, 0)
HINT_COLOR = (0, 255, 0, 128)  # Semi-transparent green for hint color

# Initialize pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Othello')

# Load images
board_img = pygame.image.load('board.png')
board_img = pygame.transform.scale(board_img, (WIDTH, WIDTH))

# Load font
font = pygame.font.Font(None, 36)

# Function to initialize the board
def initialize_board():
    board = [[0] * COLS for _ in range(ROWS)]
    board[3][3] = board[4][4] = 1
    board[3][4] = board[4][3] = -1
    return board

# Function to draw the board
def draw_board(board):
    screen.blit(board_img, (0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == 1:
                pygame.draw.circle(screen, BLACK, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 5)
            elif board[row][col] == -1:
                pygame.draw.circle(screen, WHITE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 5)

# Function to check if move is valid
def is_valid_move(board, row, col, player):
    if row < 0 or row >= ROWS or col < 0 or col >= COLS or board[row][col] != 0:
        return False
    opponent = -player
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for drow, dcol in directions:
        r, c = row + drow, col + dcol
        if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == opponent:
            r, c = r + drow, c + dcol
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == opponent:
                r, c = r + drow, c + dcol
            if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
                return True
    return False

# Function to get valid moves for a player
def get_valid_moves(board, player):
    valid_moves = []
    for row in range(ROWS):
        for col in range(COLS):
            if is_valid_move(board, row, col, player):
                valid_moves.append((row, col))
    return valid_moves

# Function to make a move
def make_move(board, row, col, player):
    board[row][col] = player
    opponent = -player
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for drow, dcol in directions:
        r, c = row + drow, col + dcol
        if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == opponent:
            r, c = r + drow, c + dcol
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == opponent:
                r, c = r + drow, c + dcol
            if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == player:
                r, c = row + drow, col + dcol
                while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == opponent:
                    board[r][c] = player
                    r, c = r + drow, c + dcol

# Function to evaluate the board for the AI
def evaluate_board(board, player):
    score = 0
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == player:
                score += 1
            elif board[row][col] == -player:
                score -= 1
    return score

# Minimax function with Alpha-Beta pruning
def minimax(board, depth, alpha, beta, maximizing_player, player):
    valid_moves = get_valid_moves(board, player)
    if depth == 0 or not valid_moves:
        return evaluate_board(board, player)
    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            new_board = copy.deepcopy(board)
            make_move(new_board, move[0], move[1], player)
            eval = minimax(new_board, depth - 1, alpha, beta, False, player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval
    else:
        min_eval = float('inf')
        for move in valid_moves:
            new_board = copy.deepcopy(board)
            make_move(new_board, move[0], move[1], -player)
            eval = minimax(new_board, depth - 1, alpha, beta, True, player)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval


# AI function to choose best move using minimax with Alpha-Beta pruning
def ai_move(board, player):
    best_move = None
    best_eval = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    valid_moves = get_valid_moves(board, player)
    for move in valid_moves:
        new_board = copy.deepcopy(board)
        make_move(new_board, move[0], move[1], player)
        eval = minimax(new_board, 4, alpha, beta, False, player)
        if eval > best_eval:
            best_eval = eval
            best_move = move
        alpha = max(alpha, eval)
    return best_move

# Function to display scores
def display_scores(screen, board):
    black_count = sum(row.count(1) for row in board)
    white_count = sum(row.count(-1) for row in board)
    
    # Clear the area where the score text will be displayed
    pygame.draw.rect(screen, GREEN, (0, 600, WIDTH, HEIGHT - 600))
    score_text = font.render("Black: {}    White: {}".format(black_count, white_count), True, WHITE)
    screen.blit(score_text, (10, 610))


# Function to display hints
def display_hint(screen, board, player):
    valid_moves = get_valid_moves(board, player)
    for move in valid_moves:
        pygame.draw.circle(screen, RED, (move[1] * SQUARE_SIZE + SQUARE_SIZE // 2, move[0] * SQUARE_SIZE + SQUARE_SIZE // 2), 5)

# Main game loop
def main():
    board = initialize_board()
    player = 1
    no_valid_moves_count = 0  # Initialize counter for consecutive no valid moves
    running = True

    while running:
        draw_board(board)
        display_scores(screen, board)
        if player == 1:
            display_hint(screen, board, player)
        pygame.display.update()
        valid_moves = get_valid_moves(board, player)
        if not valid_moves:  # Check if there are no valid moves for the current player
            print("No valid moves for player 1. Switching turn...")
            no_valid_moves_count += 1
            player *= -1
            continue  # Skip the rest of the loop and switch to the next player
        else:
            no_valid_moves_count = 0  # Reset counter for consecutive no valid moves
            if player == 1:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        col = x // SQUARE_SIZE
                        row = y // SQUARE_SIZE
                        if is_valid_move(board, row, col, player):
                            make_move(board, row, col, player)
                            player *= -1
            else:
                pygame.time.wait(500)  # Delay for 0.5 second before AI move
                move = ai_move(board, player)
                if move:
                    make_move(board, move[0], move[1], player)
                    player *= -1

        if no_valid_moves_count >= 2 or sum(row.count(0) for row in board) == 0:
            black_count = sum(row.count(1) for row in board)
            white_count = sum(row.count(-1) for row in board)
            if black_count > white_count:
                print("Black wins!")
            elif black_count < white_count:
                print("White wins!")
            else:
                print("It's a tie!")
            draw_board(board)
            display_scores(screen, board)
            pygame.display.update()
            # Wait for the player to press SPACE
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        sys.exit()

if __name__ == '__main__':
    main()






