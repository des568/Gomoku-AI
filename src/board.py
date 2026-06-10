import numpy as np

class Board:
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __init__(self, size=15):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)
        self.current_player = Board.BLACK
        self._move_history = []

    @property
    def last_move(self):
        return self._move_history[-1] if self._move_history else None

    @last_move.setter
    def last_move(self, value):
        if value is None:
            self._move_history.clear()
        else:
            self._move_history.append(value)

    def reset(self):
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_player = Board.BLACK
        self._move_history.clear()

    def is_valid_move(self, row, col):
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        return self.board[row][col] == Board.EMPTY

    def make_move(self, row, col):
        if not self.is_valid_move(row, col):
            return False

        self.board[row][col] = self.current_player
        self._move_history.append((row, col))
        self.current_player = Board.WHITE if self.current_player == Board.BLACK else Board.BLACK
        return True

    def undo_move(self):
        if not self._move_history:
            return False

        row, col = self._move_history.pop()
        self.board[row][col] = Board.EMPTY
        self.current_player = Board.WHITE if self.current_player == Board.BLACK else Board.BLACK
        return True

    def check_win(self, row, col):
        player = self.board[row][col]
        if player == Board.EMPTY:
            return False

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 1

            r, c = row + dx, col + dy
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r += dx
                c += dy

            r, c = row - dx, col - dy
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r -= dx
                c -= dy

            if count >= 5:
                return True

        return False

    def is_full(self):
        return np.all(self.board != Board.EMPTY)

    def get_empty_positions(self):
        positions = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == Board.EMPTY:
                    positions.append((row, col))
        return positions

    def get_candidates(self, radius=1):
        candidates = set()
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] != Board.EMPTY:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == Board.EMPTY:
                                candidates.add((nr, nc))
        return list(candidates) if candidates else self.get_empty_positions()

    def __str__(self):
        result = ""
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == Board.EMPTY:
                    result += ". "
                elif self.board[row][col] == Board.BLACK:
                    result += "● "
                else:
                    result += "○ "
            result += "\n"
        return result
