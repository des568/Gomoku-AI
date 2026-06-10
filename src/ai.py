import math
import time

class AI:
    def __init__(self, depth=4):
        self.depth = depth
        self.evaluator = Evaluator()
        self.best_move = None
        self.nodes_searched = 0
        self.ai_player = None  # AI执哪一方（白棋）
    
    def set_depth(self, depth):
        self.depth = depth
    
    def get_best_move(self, board):
        self.best_move = None
        self.nodes_searched = 0
        
        # AI总是执白棋（后手）
        self.ai_player = Board.WHITE
        
        candidates = board.get_candidates(radius=1)
        
        if not candidates:
            return None
        
        best_score = -math.inf
        
        for move in candidates:
            board.make_move(move[0], move[1])
            # AI是最大化玩家（白棋），所以这里传入False表示当前是最小化玩家（黑棋）的回合
            score = self.minimax(board, self.depth - 1, -math.inf, math.inf, False)
            board.undo_move()
            
            if score > best_score:
                best_score = score
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
            # AI回合（白棋），最大化分数
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
            # 玩家回合（黑棋），最小化分数
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

from evaluation import Evaluator