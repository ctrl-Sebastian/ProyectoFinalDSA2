import copy
import enum
import textwrap
import itertools

from typing import Optional
from dataclasses import dataclass

from vector2 import Vector2

@dataclass
class Move:
    beg: Vector2
    end: Vector2
    eats: [Vector2]

    def concat(self, other):
        return Move(self.beg, other.end, self.eats + other.eats)

class Team(enum.Enum):
    WHITE = 1
    BLACK = -1

    def next(self):
        return Team.WHITE if self == Team.BLACK else Team.BLACK

class Piece:
    def __init__(self, team: Team):
        self.king = False
        self.team = team

    def is_enemy(self, other):
        return False if not other else other.team != self.team

class Board:
    def __init__(self, size):
        self.player = Team.WHITE

        self.size = size
        self.matrix = [[None] * self.size for _ in range(self.size)]

        half = self.size // 2
        valid = lambda a, b: (a % 2 == 0) ^ (b % 2 == 0)

        for y in range(half - 1):
            for x in range(self.size):
                if valid(x, y):
                    self.matrix[y][x] = Piece(Team.WHITE)

        for y in range(half + 1, self.size):
            for x in range(self.size):
                if valid(x, y):
                    self.matrix[y][x] = Piece(Team.BLACK)

    def __str__(self):
        table = { Team.WHITE: "W", Team.BLACK: "B" }
        matrix = " ".join(table[cell.team] if cell else "_" for row in self.matrix for cell in row)
        return "\n".join(textwrap.wrap(matrix, self.size * 2 - 1))

    def contains(self, pos: Vector2) -> bool:
        return 0 <= pos.x < self.size and 0 <= pos.y < self.size

    def at(self, pos: Vector2) -> Optional[Piece]:
        return self.matrix[pos.y][pos.x]

    def play(self, move: Move):
        self.matrix[move.end.y][move.end.x] = self.at(move.beg)
        self.matrix[move.beg.y][move.beg.x] = None

        king_row = self.size - 1 if self.player == Team.WHITE else 0

        if move.end.y == king_row:
            self.matrix[move.end.y][move.end.x].king = True

        for eat in move.eats:
            self.matrix[eat.y][eat.x] = None

        self.player = self.player.next()

    def get_moves(self) -> [Move]:
        normal = []
        capture = []

        for y in range(self.size):
            for x in range(self.size):
                if (piece := self.matrix[y][x]) and piece.team == self.player:
                    normal.extend(self.__get_normal_moves(Vector2(x, y)))
                    capture.extend(self.__get_capture_moves(Vector2(x, y)))

        if capture:
            return capture

        return normal

    def __get_adjacent(self, pos: Vector2, piece: Piece) -> [Vector2]:
        delta_xs = (-1, 1)
        delta_ys = (-1, 1) if piece.king else (piece.team.value,)
        deltas = (Vector2(*delta) for delta in itertools.product(delta_xs, delta_ys))
        return list(filter(self.contains, (delta + pos for delta in deltas)))

    def __get_normal_moves(self, pos: Vector2) -> [Move]:
        if piece := self.at(pos):
            adjacent = self.__get_adjacent(pos, piece)
            # Create moves for each adjacent position that is not occupied
            return [Move(pos, adj, []) for adj in adjacent if not self.at(adj)]
        return []

    def __get_capture_moves(self, pos: Vector2) -> [Move]:
        return self.__get_capture_moves_rec(pos, self.at(pos), [])

    def __get_capture_moves_rec(self, pos: Vector2, piece: Piece, blacklist: [Vector2]) -> [Move]:
        result = []

        firsts = self.__get_simple_capture_moves(pos, piece, blacklist)

        for first in firsts:
            seconds = self.__get_capture_moves_rec(first.end, piece, blacklist + first.eats)
            if seconds:
                result.extend(map(first.concat, seconds))
            else:
                result.append(first)

        return result

    def __get_simple_capture_moves(self, pos: Vector2, piece: Piece, blacklist: [Vector2]) -> [Move]:
        result = []

        for adj in self.__get_adjacent(pos, piece):
            end = 2 * adj - pos

            if not self.contains(end) or self.at(end) or adj in blacklist:
                continue

            if (other := self.at(adj)) and piece.is_enemy(other):
                result.append(Move(pos, end, [adj]))

        return result

# --------
    def is_game_over(self) -> bool:
        has_white = False
        has_black = False
        for row in self.matrix:
            for piece in row:
                if piece is not None:
                    if piece.team == Team.WHITE:
                        has_white = True
                    elif piece.team == Team.BLACK:
                        has_black = True


        return has_white != has_black

    def simulate_move(self, move):
        # Create a deep copy of the board to simulate the move on
        new_board = copy.deepcopy(self)
        # Apply the move on the new board
        new_board.play(move)
        return new_board

    def evaluate_board(self):
        score = 0
        for row in self.matrix:
            for piece in row:
                if piece is not None:
                    if piece.team == Team.WHITE:  # AI
                        score += 10
                        if piece.king:
                            score += 10
                    elif piece.team == Team.BLACK:  # User
                        score -= 10
                        if piece.king:
                            score -= 10
        return score  # Return the calculated score

    def minimax(self, depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
        # Base case: evaluate the board if we have reached the maximum depth or if the game is over
        if depth == 0 or self.is_game_over():
            return self.evaluate_board(), None  # Return the evaluation score and no move

        if maximizing_player:
            # Maximizing player (AI, White)
            max_eval = float('-inf')  # Initialize to negative infinity
            best_move = None
            for move in self.get_moves():  # Get all valid moves for the AI
                # Simulate the move
                new_board = self.simulate_move(move)
                # Recursively call minimax to evaluate this move
                eval, _ = new_board.minimax(depth - 1, False, alpha, beta)
                # Choose the move with the highest evaluation
                if eval > max_eval:
                    max_eval = eval
                    best_move = move

                # Alpha-beta pruning
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break  # Stop searching this branch

            return max_eval, best_move
        else:
            # Minimizing player (Human, Black)
            min_eval = float('inf')  # Initialize to positive infinity
            best_move = None
            for move in self.get_moves():  # Get all valid moves for the opponent
                # Simulate the move
                new_board = self.simulate_move(move)
                # Recursively call minimax to evaluate this move
                eval, _ = new_board.minimax(depth - 1, True, alpha, beta)
                # Choose the move with the lowest evaluation
                if eval < min_eval:
                    min_eval = eval
                    best_move = move

                # Alpha-beta pruning
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break  # Stop searching this branch

            return min_eval, best_move

