import math

from board import Board
from evaluation import Evaluator


class AI:
    K_TOP = {2: 12, 4: 10, 6: 8}       # 顶层候选：深度越深越少
    K_INNER = {2: 8, 4: 6, 6: 5}        # 内层候选

    def __init__(self, depth=2):
        self.depth = depth
        self.evaluator = Evaluator()
        self.best_move = None
        self.nodes_searched = 0
        self.ai_player = Board.WHITE
        self._top_k = AI.K_TOP.get(depth, 10)
        self._inner_k = AI.K_INNER.get(depth, 6)

    def set_depth(self, depth):
        self.depth = depth
        self._top_k = AI.K_TOP.get(depth, 8)
        self._inner_k = AI.K_INNER.get(depth, 5)

    def get_best_move(self, board):
        self.best_move = None
        self.nodes_searched = 0

        candidates = board.get_candidates(radius=2)
        if not candidates:
            return None

        # === 优先检测：AI 能否立即获胜 ===
        for move in candidates:
            if board.is_valid_move(move[0], move[1]):
                if self._is_win(board, move, self.ai_player):
                    return move

        # === 优先检测：对手是否有杀招需要堵 ===
        opponent = Board.BLACK if self.ai_player == Board.WHITE else Board.WHITE
        opponent_wins = []
        for move in candidates:
            if board.is_valid_move(move[0], move[1]):
                if self._is_win(board, move, opponent):
                    opponent_wins.append(move)
        if opponent_wins:
            if len(opponent_wins) == 1:
                return opponent_wins[0]
            # 对面有多处杀招，选对自己最有利的
            best_block = opponent_wins[0]
            best_block_score = -math.inf
            for move in opponent_wins:
                board.make_move(move[0], move[1])
                s = self.evaluator.fast_score(board, move, self.ai_player)
                board.undo_move()
                if s > best_block_score:
                    best_block_score = s
                    best_block = move
            return best_block

        # === 使用 fast_score 排序候选 ===
        scored = []
        for move in candidates:
            s = self.evaluator.fast_score(board, move, self.ai_player)
            scored.append((s, move))
        scored.sort(key=lambda x: x[0], reverse=True)
        scored = scored[:self._top_k]

        # === Minimax 搜索 ===
        best_score = -math.inf
        for _, move in scored:
            board.make_move(move[0], move[1])
            eval_score = self._minimax(board, self.depth - 1, -math.inf, math.inf, False)
            board.undo_move()
            if eval_score > best_score or self.best_move is None:
                best_score = eval_score
                self.best_move = move

        return self.best_move if self.best_move else scored[0][1]

    def _minimax(self, board, depth, alpha, beta, maximizing):
        self.nodes_searched += 1

        if board.last_move is not None:
            if board.check_win(board.last_move[0], board.last_move[1]):
                return math.inf if board.board[board.last_move[0]][board.last_move[1]] == self.ai_player else -math.inf

        if board.is_full():
            return 0

        if depth == 0:
            return self.evaluator.evaluate(board, self.ai_player)

        candidates = board.get_candidates(radius=1)
        if not candidates:
            return self.evaluator.evaluate(board, self.ai_player)

        # 使用 fast_score 排序并限制候选数
        if len(candidates) > self._inner_k:
            scored = []
            for m in candidates:
                s = self.evaluator.fast_score(board, m, self.ai_player)
                scored.append((s, m))
            # 最大化时降序、最小化时升序（优先考虑对手的最优应手）
            scored.sort(key=lambda x: x[0], reverse=maximizing)
            candidates = [m for _, m in scored[:self._inner_k]]

        if maximizing:
            max_eval = -math.inf
            for m in candidates:
                board.make_move(m[0], m[1])
                v = self._minimax(board, depth - 1, alpha, beta, False)
                board.undo_move()
                max_eval = max(max_eval, v)
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for m in candidates:
                board.make_move(m[0], m[1])
                v = self._minimax(board, depth - 1, alpha, beta, True)
                board.undo_move()
                min_eval = min(min_eval, v)
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return min_eval

    def _is_win(self, board, move, player):
        """检查某落子是否直接形成五连"""
        board.board[move[0]][move[1]] = player
        result = board.check_win(move[0], move[1])
        board.board[move[0]][move[1]] = Board.EMPTY
        return result
