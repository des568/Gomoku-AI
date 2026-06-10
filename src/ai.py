import math
import time

from board import Board
from evaluation import Evaluator

MAX_TOP_CANDIDATES = 15
MAX_INNER_CANDIDATES = 10


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

        candidates = board.get_candidates(radius=1)
        if not candidates:
            return None

        # 启发式排序并限制候选数量
        scored = []
        for move in candidates:
            board.make_move(move[0], move[1])
            scored.append((self.evaluator.evaluate(board, self.ai_player), move))
            board.undo_move()
        scored.sort(key=lambda x: x[0], reverse=True)
        scored = scored[:MAX_TOP_CANDIDATES]

        best_score = -math.inf
        for _, move in scored:
            board.make_move(move[0], move[1])
            eval_score = self.minimax(board, self.depth - 1, -math.inf, math.inf, False)
            board.undo_move()
            if eval_score > best_score or self.best_move is None:
                best_score = eval_score
                self.best_move = move

        return self.best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        self.nodes_searched += 1

        if board.last_move is not None:
            if board.check_win(board.last_move[0], board.last_move[1]):
                return math.inf if board.board[board.last_move[0]][board.last_move[1]] == self.ai_player else -math.inf

        if board.is_full():
            return 0

        if depth == 0:
            return self.evaluator.evaluate(board, self.ai_player)

        # 获取候选并排序限制
        candidates = board.get_candidates(radius=1)
        if len(candidates) > MAX_INNER_CANDIDATES:
            scored = []
            for move in candidates:
                board.make_move(move[0], move[1])
                scored.append((self.evaluator.evaluate(board, self.ai_player), move))
                board.undo_move()
            scored.sort(key=lambda x: x[0], reverse=not maximizing_player)
            candidates = [m for _, m in scored[:MAX_INNER_CANDIDATES]]

        if maximizing_player:
            max_eval = -math.inf
            for move in candidates:
                board.make_move(move[0], move[1])
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.undo_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in candidates:
                board.make_move(move[0], move[1])
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval