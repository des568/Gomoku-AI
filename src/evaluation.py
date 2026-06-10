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
        score = 0
        opponent = Board.WHITE if player == Board.BLACK else Board.BLACK

        # 位置权重
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

                    # 找到该方向线的起点
                    r, c = row, col
                    while 0 <= r - dx < board.size and 0 <= c - dy < board.size:
                        r -= dx
                        c -= dy

                    # 提取整条线
                    line = []
                    positions = []
                    tr, tc = r, c
                    while 0 <= tr < board.size and 0 <= tc < board.size:
                        positions.append((tr, tc))
                        line.append(board.board[tr][tc])
                        tr += dx
                        tc += dy

                    # 标记已处理
                    for pos in positions:
                        processed.add(pos)

                    # 对这条线评分（长度>=5才可能成五连）
                    if len(line) >= 5:
                        player_pattern = self._create_pattern(line, player)
                        opp_pattern = self._create_pattern(line, opponent)
                        score += self._line_score(player_pattern)
                        score -= self._line_score(opp_pattern)

        return score

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
        """对一条线的模式字符串评分，使用非重叠最优匹配"""
        # 优先检测五连（获胜条件），避免被周围模式误匹配
        if '11111' in pattern:
            return Evaluator.FIVE

        total = 0
        i = 0
        # 按分数降序排序，每个位置取最高分匹配
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
