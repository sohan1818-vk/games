import pygame
import sys
import os
import urllib.request

# --- GAME LOGIC CLASS ---
class ChessGame:
    def __init__(self):
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        self.turn = 'white'
        self.castling_rights = {
            'white': {'K': True, 'Q': True},
            'black': {'K': True, 'Q': True}
        }
        self.en_passant_target = None
        self.last_move = None # To track for highlighting

    def get_piece_color(self, piece):
        if piece is None: return None
        return 'white' if piece.isupper() else 'black'

    def is_path_clear(self, start, end):
        r1, c1 = start
        r2, c2 = end
        dr = (r2 - r1) // max(abs(r2 - r1), 1)
        dc = (c2 - c1) // max(abs(c2 - c1), 1)
        r, c = r1 + dr, c1 + dc
        while (r, c) != (r2, c2):
            if self.board[r][c] is not None: return False
            r += dr
            c += dc
        return True

    def is_valid_move(self, start, end):
        r1, c1 = start
        r2, c2 = end
        piece = self.board[r1][c1]
        if piece is None: return False
        color = self.get_piece_color(piece)
        if color != self.turn: return False
        target = self.board[r2][c2]
        if target is not None and self.get_piece_color(target) == color: return False

        dr, dc = r2 - r1, c2 - c1
        abs_dr, abs_dc = abs(dr), abs(dc)
        p_type = piece.lower()

        if p_type == 'p':
            direction = -1 if color == 'white' else 1
            start_row = 6 if color == 'white' else 1
            if dc == 0 and dr == direction and target is None: return True
            if dc == 0 and dr == 2 * direction and r1 == start_row and target is None:
                if self.board[r1 + direction][c1] is None: return True
            if abs_dc == 1 and dr == direction:
                if target is not None and self.get_piece_color(target) != color: return True
                if (r2, c2) == self.en_passant_target: return True
            return False

        if p_type == 'n': return (abs_dr, abs_dc) in [(1, 2), (2, 1)]
        if p_type == 'b': return abs_dr == abs_dc and self.is_path_clear(start, end)
        if p_type == 'r': return (dr == 0 or dc == 0) and self.is_path_clear(start, end)
        if p_type == 'q': return (abs_dr == abs_dc or dr == 0 or dc == 0) and self.is_path_clear(start, end)
        if p_type == 'k':
            if max(abs_dr, abs_dc) == 1: return True
            if dr == 0 and abs_dc == 2: return self.can_castle(color, 'K' if dc > 0 else 'Q')
            return False
        return False

    def can_castle(self, color, side):
        if not self.castling_rights[color][side]: return False
        row = 7 if color == 'white' else 0
        if self.is_in_check(color): return False
        if side == 'K':
            if self.board[row][5] is not None or self.board[row][6] is not None: return False
            if self.is_square_attacked((row, 5), 'black' if color == 'white' else 'white'): return False
            return True
        elif side == 'Q':
            if self.board[row][1] is not None or self.board[row][2] is not None or self.board[row][3] is not None: return False
            if self.is_square_attacked((row, 3), 'black' if color == 'white' else 'white'): return False
            return True
        return False

    def is_square_attacked(self, square, by_color):
        r, c = square
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and self.get_piece_color(piece) == by_color:
                    original_turn = self.turn
                    self.turn = by_color
                    if self.is_valid_move((i, j), square):
                        self.turn = original_turn
                        return True
                    self.turn = original_turn
        return False

    def is_in_check(self, color):
        king_pos = None
        king_char = 'K' if color == 'white' else 'k'
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == king_char:
                    king_pos = (i, j)
                    break
            if king_pos: break
        if not king_pos: return False
        return self.is_square_attacked(king_pos, 'black' if color == 'white' else 'white')

    def make_move(self, start, end):
        r1, c1 = start
        r2, c2 = end
        piece = self.board[r1][c1]
        color = self.get_piece_color(piece)

        if piece.lower() == 'p' and (r2, c2) == self.en_passant_target:
            self.board[r1][c2] = None

        if piece.lower() == 'k' and abs(c2 - c1) == 2:
            row = r1
            if c2 > c1:
                self.board[row][5] = self.board[row][7]
                self.board[row][7] = None
            else:
                self.board[row][3] = self.board[row][0]
                self.board[row][0] = None

        self.board[r2][c2] = piece
        self.board[r1][c1] = None
        self.last_move = (start, end) # Record for highlighting

        if piece.lower() == 'p' and (r2 == 0 or r2 == 7):
            self.board[r2][c2] = 'Q' if color == 'white' else 'q'

        if piece.lower() == 'k':
            self.castling_rights[color]['K'] = False
            self.castling_rights[color]['Q'] = False
        if piece.lower() == 'r':
            if c1 == 7: self.castling_rights[color]['K'] = False
            if c1 == 0: self.castling_rights[color]['Q'] = False

        self.en_passant_target = None
        if piece.lower() == 'p' and abs(r2 - r1) == 2:
            self.en_passant_target = ((r1 + r2) // 2, c1)

        self.turn = 'black' if self.turn == 'white' else 'white'


# --- PYGAME GRAPHICS SETUP ---

def download_assets():
    os.makedirs("chess_assets", exist_ok=True)
    pieces = ['p', 'r', 'n', 'b', 'q', 'k']
    colors = ['w', 'b']
    
    # Using high-quality traditional "Staunton" pieces from Chessboard.js
    base_url = "https://chessboardjs.com/img/chesspieces/wikipedia/"
    
    for color in colors:
        for piece in pieces:
            filename = f"{color}{piece.upper()}.png" # e.g., wK.png, bP.png
            filepath = os.path.join("chess_assets", filename)
            if not os.path.exists(filepath):
                print(f"Downloading {filename}...")
                try:
                    urllib.request.urlretrieve(base_url + filename, filepath)
                except Exception as e:
                    print(f"Error downloading {filename}: {e}")

download_assets()
pygame.init()

# We add a bit of padding to the window for coordinates
BOARD_SIZE = 800
PADDING = 40
WIDTH, HEIGHT = BOARD_SIZE + PADDING * 2, BOARD_SIZE + PADDING * 2
SQUARE_SIZE = BOARD_SIZE // 8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Classic Tournament Chess")

# Classic Wooden Board Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
LAST_MOVE_COLOR = (205, 210, 106) # Subtle yellow/green tint
TEXT_COLOR = (50, 50, 50)
BG_COLOR = (49, 46, 43) # Dark background outside the board

# Load and scale piece images
pieces = {}
for color in ['w', 'b']:
    for p in ['P', 'R', 'N', 'B', 'Q', 'K']:
        img_path = os.path.join("chess_assets", f"{color}{p}.png")
        img = pygame.image.load(img_path).convert_alpha()
        pieces[f"{color}{p}"] = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))

piece_map = {
    'P': 'wP', 'R': 'wR', 'N': 'wN', 'B': 'wB', 'Q': 'wQ', 'K': 'wK',
    'p': 'bP', 'r': 'bR', 'n': 'bN', 'b': 'bB', 'q': 'bQ', 'k': 'bK'
}

def main():
    game = ChessGame()
    selected_square = None
    valid_moves = []
    running = True
    game_over = False
    font = pygame.font.SysFont('Helvetica', 24, bold=True)
    end_font = pygame.font.SysFont('Helvetica', 50, bold=True)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = pygame.mouse.get_pos()
                # Translate mouse click to board coordinates (accounting for padding)
                col = (x - PADDING) // SQUARE_SIZE
                row = (y - PADDING) // SQUARE_SIZE
                
                if 0 <= row < 8 and 0 <= col < 8:
                    if selected_square is None:
                        piece = game.board[row][col]
                        if piece and game.get_piece_color(piece) == game.turn:
                            selected_square = (row, col)
                            valid_moves = []
                            for r in range(8):
                                for c in range(8):
                                    if game.is_valid_move(selected_square, (r, c)):
                                        orig_board = [row[:] for row in game.board]
                                        orig_turn = game.turn
                                        game.make_move(selected_square, (r, c))
                                        if not game.is_in_check(orig_turn):
                                            valid_moves.append((r, c))
                                        game.board = orig_board
                                        game.turn = orig_turn
                    else:
                        start = selected_square
                        end = (row, col)
                        
                        if end in valid_moves:
                            game.make_move(start, end)
                            selected_square = None
                            valid_moves = []
                            
                            # Check for game over
                            has_moves = False
                            for r in range(8):
                                for c in range(8):
                                    if game.board[r][c] and game.get_piece_color(game.board[r][c]) == game.turn:
                                        for tr in range(8):
                                            for tc in range(8):
                                                if game.is_valid_move((r, c), (tr, tc)):
                                                    orig_board = [row[:] for row in game.board]
                                                    orig_turn = game.turn
                                                    game.make_move((r, c), (tr, tc))
                                                    if not game.is_in_check(orig_turn):
                                                        has_moves = True
                                                    game.board = orig_board
                                                    game.turn = orig_turn
                                                    if has_moves: break
                                            if has_moves: break
                                    if has_moves: break
                                if has_moves: break
                            
                            if not has_moves:
                                game_over = True
                        else:
                            selected_square = None
                            valid_moves = []

        # --- DRAWING ---
        screen.fill(BG_COLOR) # Fill background

        for r in range(8):
            for c in range(8):
                # Draw board squares
                color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
                rect = pygame.Rect(PADDING + c * SQUARE_SIZE, PADDING + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, color, rect)

                # Highlight last move
                if game.last_move:
                    if (r, c) == game.last_move[0] or (r, c) == game.last_move[1]:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                        s.set_alpha(100) # Subtle
                        s.fill(LAST_MOVE_COLOR)
                        screen.blit(s, (PADDING + c * SQUARE_SIZE, PADDING + r * SQUARE_SIZE))

                # Highlight selected square
                if selected_square == (r, c):
                    s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                    s.set_alpha(150)
                    s.fill((255, 255, 0))
                    screen.blit(s, (PADDING + c * SQUARE_SIZE, PADDING + r * SQUARE_SIZE))

                # Draw pieces
                piece = game.board[r][c]
                if piece:
                    img_key = piece_map[piece]
                    screen.blit(pieces[img_key], (PADDING + c * SQUARE_SIZE, PADDING + r * SQUARE_SIZE))

                # Draw valid move dots
                if (r, c) in valid_moves:
                    if game.board[r][c] is not None:
                        pygame.draw.circle(screen, (0, 0, 0, 100), 
                                           (PADDING + c * SQUARE_SIZE + SQUARE_SIZE//2, PADDING + r * SQUARE_SIZE + SQUARE_SIZE//2), 
                                           SQUARE_SIZE//2 - 5, 5)
                    else:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        pygame.draw.circle(s, (0, 0, 0, 60), (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//6)
                        screen.blit(s, (PADDING + c * SQUARE_SIZE, PADDING + r * SQUARE_SIZE))

        # Draw Coordinates (a-h, 1-8)
        for i in range(8):
            # Letters (bottom)
            text = font.render(chr(ord('a') + i), True, LIGHT_SQUARE)
            screen.blit(text, (PADDING + i * SQUARE_SIZE + SQUARE_SIZE//2 - text.get_width()//2, HEIGHT - PADDING + 10))
            # Numbers (left)
            text = font.render(str(8 - i), True, LIGHT_SQUARE)
            screen.blit(text, (PADDING - 25, PADDING + i * SQUARE_SIZE + SQUARE_SIZE//2 - text.get_height()//2))

        # Draw Game Over Text
        if game_over:
            winner = 'Black' if game.turn == 'white' else 'White'
            if game.is_in_check(game.turn):
                text = end_font.render(f"Checkmate! {winner} wins!", True, (255, 50, 50))
            else:
                text = end_font.render("Stalemate! Draw.", True, (200, 200, 200))
            
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            pygame.draw.rect(screen, (0, 0, 0), (text_rect.x - 20, text_rect.y - 10, text_rect.width + 40, text_rect.height + 20))
            screen.blit(text, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()