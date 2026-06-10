import math

from board import Board
from evaluation import Evaluator


class AI:
    def __init__(self, depth=2):
        self.depth = depth
        self.evaluator = Evaluator()
        self.best_move = None
        self.nodes_searched = 0
        self.ai_player = Board.WHITE

    def set_depth(self, depth):
        self.depth = depth

    def get_best_move(self, board):
        self.best_move = None
        self.nodes_searched = 0
        opponent = Board.BLACK if self.ai_player == Board.WHITE else Board.WHITE

        # ===== 自适应策略：根据棋盘棋子数调整深度和候选数 =====
        stone_count = sum(1 for r in range(board.size)
                          for c in range(board.size) if board.board[r][c] != Board.EMPTY)

        if stone_count <= 4:
            effective_depth = 2
            top_k, inner_k = 8, 6
        elif stone_count <= 10:
            effective_depth = self.depth
            top_k, inner_k = 10, 8
        elif stone_count <= 16:
            effective_depth = self.depth + 1
            top_k, inner_k = 10, 8
        else:
            effective_depth = self.depth + 1
            top_k, inner_k = 12, 10

        # 简单难度始终浅搜索
        if self.depth <= 2:
            effective_depth = min(effective_depth, 3)

        # ===== 获取候选：只考虑有邻居的位置 =====
        candidates = self._get_smart_candidates(board)
        if not candidates:
            return None

        # ===== 优先检测：AI 能否直接获胜 =====
        for move in candidates:
            if self._is_win(board, move, self.ai_player):
                return move

        # ===== 优先检测：对手是否有必防点位 =====
        opp_threats = []
        for move in candidates:
            if self._is_win(board, move, opponent):
                opp_threats.append(move)

        if opp_threats:
            if len(opp_threats) == 1:
                return opp_threats[0]
            # 多处被杀，选最优
            best = opp_threats[0]
            best_s = -math.inf
            for move in opp_threats:
                board.make_move(move[0], move[1])
                s = self.evaluator.fast_score(board, move, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s = s
                    best = move
            return best

        # 检测对手活四/冲四威胁
        for move in candidates:
            if self._is_live_four(board, move, opponent):
                opp_threats.append(move)
        if opp_threats:
            # 选对自己最有利的封堵
            best = opp_threats[0]
            best_s = -math.inf
            for move in opp_threats:
                board.make_move(move[0], move[1])
                s = self.evaluator.fast_score(board, move, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s = s
                    best = move
            return best

        # ===== fast_score 排序候选 =====
        scored = []
        for move in candidates:
            s = self.evaluator.fast_score(board, move, self.ai_player)
            scored.append((s, move))
        scored.sort(key=lambda x: x[0], reverse=True)
        scored = scored[:top_k]

        # ===== Negamax 搜索 =====
        best_score = -math.inf
        for _, move in scored:
            board.make_move(move[0], move[1])
            # Negamax: 对手视角 = -negamax(对手)
            score = -self._negamax(board, effective_depth - 1, -math.inf, -best_score, opponent)
            board.undo_move()
            if score > best_score or self.best_move is None:
                best_score = score
                self.best_move = move

        return self.best_move if self.best_move else scored[0][1]

    def _negamax(self, board, depth, alpha, beta, player):
        """负值极大搜索 + Alpha-Beta 剪枝"""
        self.nodes_searched += 1

        # 检查上一步是否获胜
        if board.last_move is not None:
            if board.check_win(board.last_move[0], board.last_move[1]):
                return -math.inf

        if board.is_full():
            return 0

        if depth == 0:
            return self.evaluator.evaluate(board, player)

        candidates = self._get_smart_candidates(board)
        if not candidates:
            return self.evaluator.evaluate(board, player)

        # 动态候选限制：越深越少
        if depth <= 2:
            nk = 6
        elif depth <= 4:
            nk = 8
        else:
            nk = 10

        # 排序并限制候选
        if len(candidates) > nk:
            scored = []
            for m in candidates:
                s = self.evaluator.fast_score(board, m, player)
                scored.append((s, m))
            scored.sort(key=lambda x: x[0], reverse=True)
            candidates = [m for _, m in scored[:nk]]

        opponent = Board.WHITE if player == Board.BLACK else Board.BLACK
        best = -math.inf

        for move in candidates:
            board.make_move(move[0], move[1])
            val = -self._negamax(board, depth - 1, -beta, -alpha, opponent)
            board.undo_move()

            if val > best:
                best = val
            if val > alpha:
                alpha = val
            if alpha >= beta:
                break

        return best

    def _get_smart_candidates(self, board):
        """只取有邻居的空位——大幅减少无效候选"""
        candidates = []
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] != Board.EMPTY:
                    continue
                if self._has_neighbor(board, row, col):
                    candidates.append((row, col))
        if candidates:
            return candidates
        # 空棋盘（第一步）走天元
        return [(7, 7)]

    def _has_neighbor(self, board, row, col):
        """检查该位置2格内是否有棋子"""
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                nr, nc = row + dr, col + dc
                if 0 <= nr < board.size and 0 <= nc < board.size:
                    if board.board[nr][nc] != Board.EMPTY:
                        return True
        return False

    def _is_win(self, board, move, player):
        board.board[move[0]][move[1]] = player
        result = board.check_win(move[0], move[1])
        board.board[move[0]][move[1]] = Board.EMPTY
        return result

    def _is_live_four(self, board, move, player):
        """检查下在move后是否形成活四或冲四"""
        row, col = move
        board.board[row][col] = player
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        is_threat = False
        for dx, dy in directions:
            # 向两个方向各检查5格
            line = []
            for i in range(-4, 5):
                r, c = row + i * dx, col + i * dy
                if 0 <= r < board.size and 0 <= c < board.size:
                    line.append(board.board[r][c])
                else:
                    line.append(-1)
            pattern = self.evaluator._create_pattern(line, player)
            # 活四或冲四
            if '011110' in pattern or '11110' in pattern or '01111' in pattern:
                is_threat = True
                break
        board.board[row][col] = Board.EMPTY
        return is_threat
