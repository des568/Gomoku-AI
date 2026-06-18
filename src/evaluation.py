from board import Board


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
        """完整局面评估——仅用于叶子节点"""
        # 进攻偏好系数：己方棋型x1.1，对手x1.0
        ATTACK_BIAS = 1.1
        score = 0
        opponent = Board.WHITE if player == Board.BLACK else Board.BLACK

        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] != Board.EMPTY:
                    score += self.center_weight[row][col] * (1 if board.board[row][col] == player else -1)

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            processed = set()
            for row in range(board.size):
                for col in range(board.size):
                    if (row, col) in processed:
                        continue
                    r, c = row, col
                    while 0 <= r - dx < board.size and 0 <= c - dy < board.size:
                        r -= dx
                        c -= dy
                    line, positions = [], []
                    tr, tc = r, c
                    while 0 <= tr < board.size and 0 <= tc < board.size:
                        positions.append((tr, tc))
                        line.append(board.board[tr][tc])
                        tr += dx
                        tc += dy
                    for pos in positions:
                        processed.add(pos)
                    if len(line) >= 5:
                        score += self._line_score(self._create_pattern(line, player)) * ATTACK_BIAS
                        score -= self._line_score(self._create_pattern(line, opponent))
        return score

    def fast_score(self, board, move, player):
        """
        轻量级位置评分——仅评估经过该位置的4条线。
        用于候选排序，比完整 evaluate 快 10 倍以上。
        """
        row, col = move
        opponent = Board.WHITE if player == Board.BLACK else Board.BLACK
        score = 0

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            # 沿该方向提取9格窗口（以落子位置为中心）
            line = []
            r, c = row - 4 * dx, col - 4 * dy
            for _ in range(9):
                if 0 <= r < board.size and 0 <= c < board.size:
                    line.append(board.board[r][c])
                else:
                    line.append(-1)  # 边界外
                r += dx
                c += dy

            if len([1 for v in line if v != -1]) >= 5:
                score += self._line_score(self._create_pattern(line, player))
                score -= self._line_score(self._create_pattern(line, opponent))

        # 中心位置奖励
        score += self.center_weight[row][col] * 20
        return score

    def is_winning_move(self, board, move, player):
        """检查某个落子是否直接获胜"""
        row, col = move
        board.board[row][col] = player
        result = board.check_win(row, col)
        board.board[row][col] = Board.EMPTY
        return result

    def _create_pattern(self, line, player):
        result = []
        for cell in line:
            if cell == player:
                result.append('1')
            elif cell == Board.EMPTY:
                result.append('0')
            else:
                result.append('x')
        return ''.join(result)

    def _line_score(self, pattern):
        if '11111' in pattern:
            return Evaluator.FIVE

        total = 0
        i = 0
        sorted_patterns = sorted(Evaluator.PATTERNS.items(),
                                 key=lambda x: (-x[1], -len(x[0])))

        while i < len(pattern):
            best_score = 0
            best_len = 1
            for key, pat_score in sorted_patterns:
                if i + len(key) <= len(pattern) and pattern[i:i + len(key)] == key:
                    best_score = pat_score
                    best_len = len(key)
                    break
            total += best_score
            i += best_len

        return total
