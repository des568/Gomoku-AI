import pygame
import sys
from threading import Thread


class UI:
    def __init__(self, board, ai):
        pygame.init()
        self.board = board
        self.ai = ai
        self.cell_size = 40
        self.board_size = 15
        self.board_pixel = self.board_size * self.cell_size + 60
        self.screen_width = self.board_pixel + 180
        self.screen_height = self.board_pixel + 40
        self.padding = 30
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Gomoku-AI 五子棋 AI")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BOARD_COLOR = (200, 160, 100)
        self.TEXT_COLOR = (50, 50, 50)

        self.font = self._get_font(22)
        self.small_font = self._get_font(16)

        self.game_over = False
        self.winner = None
        self.ai_move = None
        self.is_player_turn = True
        self.ai_result_ready = False
        self._last_player_turn = True
        self._last_game_over = False
        self._last_winner = None

        # ===== 预渲染所有静态文本，避免每帧重绘 =====
        p = self.board_pixel + 10
        self._panel_rect = pygame.Rect(p - 5, 10, 170, self.screen_height - 20)
        self._btn_restart = pygame.Rect(p, self.screen_height - 70, 75, 32)
        self._btn_undo = pygame.Rect(p + 85, self.screen_height - 70, 75, 32)

        self._txt_restart = self.font.render("重新开始", True, self.WHITE)
        self._txt_undo = self.font.render("悔棋", True, self.WHITE)
        self._txt_turn_label = self.small_font.render("状态:", True, self.TEXT_COLOR)

        # 动态文本缓存
        self._cache = {}

    def _get_font(self, size):
        fonts_to_try = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "Arial", None
        ]
        for fp in fonts_to_try:
            try:
                return pygame.font.Font(fp, size) if fp else pygame.font.Font(None, size)
            except:
                continue
        return pygame.font.Font(None, size)

    def _cached_text(self, key, render_fn):
        if key not in self._cache:
            self._cache[key] = render_fn()
        return self._cache[key]

    def draw_board(self):
        self.screen.fill(self.BOARD_COLOR)

        end = self.padding + (self.board_size - 1) * self.cell_size
        for i in range(self.board_size):
            x = self.padding + i * self.cell_size
            pygame.draw.line(self.screen, self.BLACK, (x, self.padding), (x, end), 1)
            pygame.draw.line(self.screen, self.BLACK, (self.padding, x), (end, x), 1)

        for i in [3, 7, 11]:
            x = self.padding + i * self.cell_size
            for j in [3, 7, 11]:
                pygame.draw.circle(self.screen, self.BLACK, (x, self.padding + j * self.cell_size), 4, 0)

        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board.board[r][c] != 0:
                    x = self.padding + c * self.cell_size
                    y = self.padding + r * self.cell_size
                    clr = self.BLACK if self.board.board[r][c] == 1 else self.WHITE
                    pygame.draw.circle(self.screen, clr, (x, y), self.cell_size // 2 - 2, 0)
                    if clr == self.WHITE:
                        pygame.draw.circle(self.screen, self.BLACK, (x, y), self.cell_size // 2 - 2, 1)

    def draw_ui(self):
        px, py = self.board_pixel + 10, 25

        # 面板背景
        pygame.draw.rect(self.screen, (240, 240, 240), self._panel_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), self._panel_rect, 1)

        # 状态
        self.screen.blit(self._txt_turn_label, (px, py))
        py += 25

        # 只在状态变化时重渲染
        state = (self.game_over, self.is_player_turn, self.winner)
        if state != getattr(self, '_last_state', None):
            self._last_state = state
            self._cache.pop('turn_text', None)
            self._cache.pop('result_text', None)

        if not self.game_over:
            turn = "你的回合" if self.is_player_turn else "AI 思考..."
            txt = self._cached_text('turn_text',
                                    lambda: self.small_font.render(turn, True, (70, 130, 180)))
            self.screen.blit(txt, (px, py))
        else:
            wname = "黑棋" if self.winner == 1 else ("白棋" if self.winner == 2 else "平局")
            txt = self._cached_text('result_text',
                                    lambda: self.font.render(f"{wname}获胜!" if self.winner else "平局",
                                                             True, (200, 30, 30) if self.winner else (0, 0, 200)))
            self.screen.blit(txt, (px, py))
        py += 40

        # 按钮
        pygame.draw.rect(self.screen, (60, 179, 113), self._btn_restart, border_radius=5)
        r = self._txt_restart.get_rect(center=self._btn_restart.center)
        self.screen.blit(self._txt_restart, r)

        pygame.draw.rect(self.screen, (205, 92, 92), self._btn_undo, border_radius=5)
        r = self._txt_undo.get_rect(center=self._btn_undo.center)
        self.screen.blit(self._txt_undo, r)

    def handle_click(self, pos):
        # 重新开始 —— 始终可用
        if self._btn_restart.collidepoint(pos):
            self.board.reset()
            self.game_over = False
            self.winner = None
            self.ai_move = None
            self.is_player_turn = True
            self._cache.clear()
            return

        # 悔棋 —— 仅在游戏中
        if self._btn_undo.collidepoint(pos) and not self.game_over:
            if self.board.last_move is not None:
                self.board.undo_move()
            if self.board.last_move is not None:
                self.board.undo_move()
            self.winner = None
            self.ai_move = None
            self.is_player_turn = True
            self._cache.clear()
            return

        # 棋盘落子
        if not self.is_player_turn or self.game_over:
            return
        if pos[0] > self.board_pixel:
            return

        col = round((pos[0] - self.padding) / self.cell_size)
        row = round((pos[1] - self.padding) / self.cell_size)
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return

        if self.board.make_move(row, col):
            if self.board.check_win(row, col):
                self.game_over = True
                self.winner = 1
                return
            if self.board.is_full():
                self.game_over = True
                return
            self.is_player_turn = False
            self.ai_result_ready = True

    def run(self):
        def ai_think():
            self.ai_move = self.ai.get_best_move(self.board)

        running = True

        while running:
            # ===== AI 落子 =====
            if self.ai_move is not None and not self.is_player_turn and not self.game_over:
                r, c = self.ai_move
                self.board.make_move(r, c)
                if self.board.check_win(r, c):
                    self.game_over = True
                    self.winner = 2
                self.ai_move = None
                self.is_player_turn = True

            # ===== 启动 AI 思考 =====
            if self.ai_result_ready and self.ai_move is None and not self.game_over:
                self.ai_result_ready = False
                t = Thread(target=ai_think)
                t.daemon = True
                t.start()

            # ===== 事件 =====
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(e.pos)

            # ===== 渲染 =====
            self.draw_board()
            self.draw_ui()
            pygame.display.flip()

        pygame.quit()
