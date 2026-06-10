class Evaluator:
    FIVE = 100000
    LIVE_FOUR = 10000
    BLOCKED_FOUR = 5000
    LIVE_THREE = 1000
    BLOCKED_THREE = 500
    LIVE_TWO = 100
    BLOCKED_TWO = 50
    LIVE_ONE = 10
    BLOCKED_ONE = 5
    
    PATTERNS = {
        '11111': FIVE,
        '011110': LIVE_FOUR,
        '11110': BLOCKED_FOUR,
        '01111': BLOCKED_FOUR,
        '11011': BLOCKED_FOUR,
        '01110': LIVE_THREE,
        '011010': LIVE_THREE,
        '010110': LIVE_THREE,
        '1110': BLOCKED_THREE,
        '0111': BLOCKED_THREE,
        '1101': BLOCKED_THREE,
        '1011': BLOCKED_THREE,
        '0110': LIVE_TWO,
        '01010': LIVE_TWO,
        '110': BLOCKED_TWO,
        '011': BLOCKED_TWO,
        '101': BLOCKED_TWO,
        '010': LIVE_ONE,
        '10': BLOCKED_ONE,
        '01': BLOCKED_ONE,
    }
    
    def __init__(self):
        self.center_weight = [[0] * 15 for _ in range(15)]
        for i in range(15):
            for j in range(15):
                dist = abs(i - 7) + abs(j - 7)
                self.center_weight[i][j] = max(0, 8 - dist)
    
    def evaluate(self, board, player):
        score = 0
        opponent = Board.WHITE if player == Board.BLACK else Board.BLACK
        
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] != Board.EMPTY:
                    score += self.center_weight[row][col] * (1 if board.board[row][col] == player else -1)
        
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] != Board.EMPTY:
                    for dx, dy in directions:
                        line = self._get_line(board, row, col, dx, dy)
                        player_pattern = self._create_pattern(line, player)
                        opp_pattern = self._create_pattern(line, opponent)
                        
                        score += self._pattern_to_score(player_pattern)
                        score -= self._pattern_to_score(opp_pattern)
        
        return score
    
    def _get_line(self, board, row, col, dx, dy):
        line = []
        r, c = row, col
        
        while 0 <= r - dx < board.size and 0 <= c - dy < board.size:
            r -= dx
            c -= dy
        
        while 0 <= r < board.size and 0 <= c < board.size:
            line.append(board.board[r][c])
            r += dx
            c += dy
        
        return line
    
    def _create_pattern(self, line, player):
        pattern = []
        for cell in line:
            if cell == player:
                pattern.append('1')
            elif cell == Board.EMPTY:
                pattern.append('0')
            else:
                pattern.append('x')
        
        return ''.join(pattern)
    
    def _pattern_to_score(self, pattern):
        max_score = 0
        for key, score in Evaluator.PATTERNS.items():
            if key in pattern:
                if score > max_score:
                    max_score = score
        return max_score

from board import Board