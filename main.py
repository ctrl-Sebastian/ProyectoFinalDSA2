import pygame

import checkers
from vector2 import Vector2

board = checkers.Board(8)

class Spritesheet:
    def __init__(self, sheet, colorkey):
        self.sheet = sheet
        self.colorkey = colorkey

    def read_image(self, rect):
        image = pygame.Surface(rect.size)
        image.blit(self.sheet, (0, 0), rect)
        image.set_colorkey(self.colorkey)
        return image

    def read_images(self, rects):
        return [self.read_image(rect) for rect in rects]

pygame.init()

board_image = pygame.image.load("./resources/boards/board_plain_01.png")
board_width, board_height = board_image.get_size()

assert board_width == board_height, "Invaild board format"

checkers_image_sheet = pygame.image.load("./resources/checkers_topDown.png")
checkers_spritesheet = Spritesheet(checkers_image_sheet, (0, 0, 0, 0))

checkers_rects = [pygame.Rect(16 * i, 0, 16, 16) for i in range(4)]
checkers_images = checkers_spritesheet.read_images(checkers_rects)

info = pygame.display.Info()
dimensions = info.current_w, info.current_h

scale = ((min(dimensions) // 2) // board_width + 1)

screen_size = board_width * scale

board_image = pygame.transform.scale(board_image, (screen_size, screen_size))
checkers_images = [pygame.transform.scale(checker_image, (16 * scale, 16 * scale)) for checker_image in checkers_images]

checker_size = 16 * scale
margin = (screen_size - 8 * checker_size) // 2

surface = pygame.display.set_mode((screen_size, screen_size))
clock = pygame.time.Clock()

moves = None
selected = None

done = False
while not done:
    if board.player == checkers.Team.WHITE:  # AI's turn
        _, best_move = board.minimax(8, True)  # Depth of 3, AI is the maximizing player
        if best_move:
            board.play(best_move)  # Play the best move found by the AI
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                board_x = (x - margin) // checker_size
                board_y = (y - margin) // checker_size
                selected = Vector2(board_x, board_y)

        surface.blit(board_image, (0, 0))


        if selected:
            if piece := board.at(selected):
                moves = [move for move in board.get_moves() if move.beg == selected]
                for move in moves:
                    highlight = pygame.Surface((checker_size, checker_size))
                    highlight.set_alpha(111)
                    highlight.fill("black")
                    left = margin + checker_size * move.end.x
                    top = margin + checker_size * move.end.y
                    surface.blit(highlight, (left, top))
            elif move := [move for move in moves if move.end == selected]:
                board.play(*move)
                selected = None
                moves = []

        for i in range(board.size):
            for j in range(board.size):
                if piece := board.matrix[i][j]:
                    index = 0 if piece.team == checkers.Team.WHITE else 2
                    index = index + 1 if piece.king else index
                    left = margin + j * checker_size
                    top = margin + i * checker_size
                    surface.blit(checkers_images[index], (left, top))

    pygame.display.update()

    clock.tick(60)
