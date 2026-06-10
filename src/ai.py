import math
import time

from board import Board
from evaluation import Evaluator

class AI:
    def __init__(self, depth=4):
        self.depth = depth
        self.evaluator = Evaluator()
        self.best_move = None
        self.nodes_searched = 0
        self.ai_player = Board.WHITE  # AI执白棋（后手）
    
    def set_depth(self, depth):
        self.depth = depth
    
    def get_best_move(self, board):
        self.best_move = None
        self.nodes_searched = 0
        
        candidates = board.get_candidates(radius=1)

        if not candidates:
            return None

        # 按启发式分值排序候选点，优先搜索高分位置，提升Alpha-Beta剪枝效率
        scored_candidates = []
        for move in candidates:
            board.make_move(move[0], move[1])
            heuristic_score = self.evaluator.evaluate(board, self.ai_player)
            board.undo_move()
            scored_candidates.append((heuristic_score, move))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        best_score = -math.inf

        for _, move in scored_candidates:
            board.make_move(move[0], move[1])
            eval_score = self.minimax(board, self.depth - 1, -math.inf, math.inf, False)
            board.undo_move()

            if eval_score > best_score or self.best_move is None:
                best_score = eval_score
                self.best_move = move

        return self.best_move
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        self.nodes_searched += 1
        
        # 检查胜负
        if board.last_move is not None:
            if board.check_win(board.last_move[0], board.last_move[1]):
                # 如果上一步是AI（白棋）获胜，返回正无穷
                if board.board[board.last_move[0]][board.last_move[1]] == self.ai_player:
                    return math.inf
                else:
                    return -math.inf
        
        if board.is_full():
            return 0
        
        if depth == 0:
            return self.evaluator.evaluate(board, self.ai_player)
        
        candidates = board.get_candidates(radius=1)
        
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