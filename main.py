from enum import Enum

class Team(Enum):
    NONE = 0
    CROSS = 1
    CIRCLE = 2

    def next(self):
        if self == Team.CROSS:
            return Team.CIRCLE
        return Team.CROSS

class Board:
    def __init__(self):
        self.player = Team.CROSS
        self.data = [Team.NONE for _ in range(9)]

    def play(self, index):
        self.data[index] = self.player
        self.player = self.player.next()

    def clear(self, index):
        self.data[index] = Team.NONE
        self.player = self.player.next()

    def at(self, index) -> Team:
        return self.data[index]

    def won(self) -> Team:
        magic = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 5],
            [2, 4, 6],
        ]

        for indices in magic:
            for team in [Team.CROSS, Team.CIRCLE]:
                if all(self.data[i] == team for i in indices):
                    return team

        return Team.NONE

    def hash(self):
        cross = [team == Team.CROSS for team in self.data]
        circle = [team == Team.CIRCLE for team in self.data]
        hash = cross + circle + [self.player == Team.CROSS]
        return sum(map(lambda x: x[1] << x[0], enumerate(hash)))

board = Board()

def backtrack(steps):
    global ties

    if steps == 9:
        if board.won() == Team.NONE:
            ties += 1
        return

    for i in range(9):
        if board.at(i) == Team.NONE:
            board.play(i)
            backtrack(steps + 1)
            board.clear(i)

board.hash()
