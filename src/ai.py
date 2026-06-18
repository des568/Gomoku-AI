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

        # ========== 根节点威胁检测（五子棋规则优先级）==========
        # 1. AI 直接五连 → 获胜
        # 2. 对手能五连 → 必须堵
        # 3. 对手有活四 → 必须堵（两边都要防，尽力而为）
        # 4. AI 有活四 → 下子必胜
        # 5. 对手有冲四 → 必须堵唯一胜点
        # 6. AI 有冲四 → 下子造杀
        # 7. AI 有活三 → 进攻（对手无严重威胁时）
        # ========================================================

        # 1. AI 直接获胜
        for move in candidates:
            if self._is_win(board, move, self.ai_player):
                return move

        # 2. 对手能五连 → 必须堵
        opp_wins = [m for m in candidates if self._is_win(board, m, opponent)]
        if opp_wins:
            if len(opp_wins) == 1:
                return opp_wins[0]
            best, best_s = opp_wins[0], -math.inf
            for m in opp_wins:
                board.make_move(m[0], m[1])
                s = self.evaluator.fast_score(board, m, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s, best = s, m
            return best

        # 3. 对手有活四（两端空的四连）→ 必须堵
        opp_live4 = [m for m in candidates if self._is_live_four_strict(board, m, opponent, live_only=True)]
        if opp_live4:
            best, best_s = opp_live4[0], -math.inf
            for m in opp_live4:
                board.make_move(m[0], m[1])
                s = self.evaluator.fast_score(board, m, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s, best = s, m
            return best

        # 4. AI 有活四 → 下子必胜
        ai_live4 = [m for m in candidates if self._is_live_four_strict(board, m, self.ai_player, live_only=True)]
        if ai_live4:
            best, best_s = ai_live4[0], -math.inf
            for m in ai_live4:
                board.make_move(m[0], m[1])
                s = self.evaluator.fast_score(board, m, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s, best = s, m
            return best

        # 5. 对手有冲四 → 堵唯一胜点
        opp_blocked4 = [m for m in candidates if self._is_live_four_strict(board, m, opponent, live_only=False)]
        if opp_blocked4:
            best, best_s = opp_blocked4[0], -math.inf
            for m in opp_blocked4:
                board.make_move(m[0], m[1])
                s = self.evaluator.fast_score(board, m, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s, best = s, m
            return best

        # 6. AI 有冲四 → 主动造杀
        ai_blocked4 = [m for m in candidates if self._is_live_four_strict(board, m, self.ai_player, live_only=False)]
        if ai_blocked4:
            best, best_s = ai_blocked4[0], -math.inf
            for m in ai_blocked4:
                board.make_move(m[0], m[1])
                s = self.evaluator.fast_score(board, m, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s, best = s, m
            return best

        # 7. AI 有活三 → 进攻（此时已确认对手无严重威胁）
        ai_live3 = [m for m in candidates if self._is_live_three(board, m, self.ai_player)]
        if ai_live3:
            best, best_s = ai_live3[0], -math.inf
            for m in ai_live3:
                board.make_move(m[0], m[1])
                s = self.evaluator.fast_score(board, m, self.ai_player)
                board.undo_move()
                if s > best_s:
                    best_s, best = s, m
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
        """检查下在move后是否形成活四或冲四（宽松，向后兼容）"""
        return self._is_live_four_strict(board, move, player, live_only=False)

    def _is_live_four_strict(self, board, move, player, live_only=True):
        """
        严格检测四子威胁。
        live_only=True: 只检测活四（011110），两端都有空
        live_only=False: 检测所有四子（活四、冲四）
        """
        row, col = move
        board.board[row][col] = player
        result = False
        for dx, dy in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            line = []
            for i in range(-5, 6):  # ±5 = 11格窗口
                r, c = row + i * dx, col + i * dy
                if 0 <= r < board.size and 0 <= c < board.size:
                    line.append(board.board[r][c])
                else:
                    line.append(-1)
            p = self.evaluator._create_pattern(line, player)
            if live_only:
                # 只检测活四：011110（两端都空）
                if '011110' in p:
                    result = True
                    break
            else:
                # 冲四：一侧堵一侧空
                if '011110' in p or '11110' in p or '01111' in p or '11011' in p or '10111' in p or '11101' in p:
                    result = True
                    break
        board.board[row][col] = Board.EMPTY
        return result

    def _is_live_three(self, board, move, player):
        """检查下在move后是否形成活三（三连，两端各有2+空格可延伸）"""
        row, col = move
        board.board[row][col] = player
        result = False
        for dx, dy in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            line = []
            for i in range(-5, 6):
                r, c = row + i * dx, col + i * dy
                if 0 <= r < board.size and 0 <= c < board.size:
                    line.append(board.board[r][c])
                else:
                    line.append(-1)
            p = self.evaluator._create_pattern(line, player)
            # 活三: 三连两端都有空位可延伸
            # 01110: 连续三子
            # 010110: 跳活三 O X O O X O
            # 011010: 跳活三 O O X O X O
            if '01110' in p or '010110' in p or '011010' in p:
                result = True
                break
        board.board[row][col] = Board.EMPTY
        return result
