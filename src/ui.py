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
        self.screen_width = self.board_pixel + 200
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

        self.selected_depth = 2
        self.depths = [2, 4, 6]
        self.game_over = False
        self.winner = None
        self.ai_move = None
        self.is_player_turn = True
        self.ai_result_ready = False

        # 缓存按钮区域
        self._cached_buttons = {}

    def _get_font(self, size):
        fonts_to_try = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
            "Arial",
            None
        ]
        for font_path in fonts_to_try:
            try:
                if font_path is None:
                    return pygame.font.Font(None, size)
                return pygame.font.Font(font_path, size)
            except:
                continue
        return pygame.font.Font(None, size)

    def _compute_buttons(self):
        """仅计算按钮位置，不渲染"""
        panel_x = self.board_pixel + 10
        panel_y = 30

        # 跳过文本，直接计算
        panel_y += 35  # 当前回合文本
        panel_y += 22  # 难度标签

        depth_buttons = []
        for _ in self.depths:
            btn_rect = pygame.Rect(panel_x, panel_y, 55, 25)
            depth_buttons.append(btn_rect)
            panel_y += 30

        panel_y += 15
        btn_width, btn_height = 80, 32
        restart_btn = pygame.Rect(panel_x, panel_y, btn_width, btn_height)
        undo_btn = pygame.Rect(panel_x + btn_width + 10, panel_y, btn_width, btn_height)

        return {
            'depth_buttons': depth_buttons,
            'restart_btn': restart_btn,
            'undo_btn': undo_btn
        }

    def draw_board(self):
        self.screen.fill(self.BOARD_COLOR)

        # 棋盘线
        line_end = self.padding + (self.board_size - 1) * self.cell_size
        for i in range(self.board_size):
            x = self.padding + i * self.cell_size
            pygame.draw.line(self.screen, self.BLACK, (x, self.padding), (x, line_end), 1)
            pygame.draw.line(self.screen, self.BLACK, (self.padding, x), (line_end, x), 1)

        # 星位
        for i in [3, 7, 11]:
            x = self.padding + i * self.cell_size
            for j in [3, 7, 11]:
                y = self.padding + j * self.cell_size
                pygame.draw.circle(self.screen, self.BLACK, (x, y), 4, 0)

        # 棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board.board[row][col] != 0:
                    x = self.padding + col * self.cell_size
                    y = self.padding + row * self.cell_size
                    color = self.BLACK if self.board.board[row][col] == 1 else self.WHITE
                    pygame.draw.circle(self.screen, color, (x, y), self.cell_size // 2 - 2, 0)
                    if color == self.WHITE:
                        pygame.draw.circle(self.screen, self.BLACK, (x, y), self.cell_size // 2 - 2, 1)

    def draw_ui(self):
        panel_x = self.board_pixel + 10
        panel_y = 30
        panel_width = 180

        # 面板背景
        panel_rect = pygame.Rect(panel_x - 5, 10, panel_width, self.screen_height - 20)
        pygame.draw.rect(self.screen, (240, 240, 240), panel_rect)
        pygame.draw.rect(self.screen, (180, 180, 180), panel_rect, 1)

        current_x = panel_x

        # 当前回合
        if self.game_over:
            current_player = "游戏结束"
        elif self.is_player_turn:
            current_player = "玩家回合"
        else:
            current_player = "AI思考中..."
        current_text = self.font.render(f"当前: {current_player}", True, self.TEXT_COLOR)
        self.screen.blit(current_text, (current_x, panel_y))
        panel_y += 35

        # 难度
        difficulty_label = self.small_font.render("难度:", True, self.TEXT_COLOR)
        self.screen.blit(difficulty_label, (current_x, panel_y))
        panel_y += 22

        depth_buttons = []
        for i, depth in enumerate(self.depths):
            btn_rect = pygame.Rect(current_x, panel_y, 55, 25)
            depth_buttons.append(btn_rect)
            is_selected = self.selected_depth == depth
            color = (70, 130, 180) if is_selected else (220, 220, 220)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)
            depth_names = {2: "简单", 4: "中等", 6: "困难"}
            text = self.small_font.render(f"{depth_names[depth]}", True,
                                          self.WHITE if is_selected else self.TEXT_COLOR)
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)
            panel_y += 30

        panel_y += 15
        btn_width, btn_height = 80, 32

        # 重新开始按钮
        restart_btn = pygame.Rect(current_x, panel_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, (60, 179, 113), restart_btn, border_radius=5)
        restart_text = self.font.render("重新开始", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=restart_btn.center)
        self.screen.blit(restart_text, restart_rect)

        # 悔棋按钮
        undo_btn = pygame.Rect(current_x + btn_width + 10, panel_y, btn_width, btn_height)
        pygame.draw.rect(self.screen, (205, 92, 92), undo_btn, border_radius=5)
        undo_text = self.font.render("悔棋", True, self.WHITE)
        undo_rect = undo_text.get_rect(center=undo_btn.center)
        self.screen.blit(undo_text, undo_rect)
        panel_y += 45

        # 游戏结果
        if self.game_over:
            panel_y += 20
            winner_name = "黑棋" if self.winner == 1 else ("白棋" if self.winner == 2 else "平局")
            result_color = (255, 0, 0) if self.winner else (0, 0, 255)
            result_text = self.font.render(f"游戏结束!", True, result_color)
            self.screen.blit(result_text, (current_x, panel_y))
            panel_y += 30
            winner_text = self.font.render(f"{winner_name}获胜!", True, result_color)
            self.screen.blit(winner_text, (current_x, panel_y))

        self._cached_buttons = {
            'depth_buttons': depth_buttons,
            'restart_btn': restart_btn,
            'undo_btn': undo_btn
        }

    def handle_click(self, pos):
        if not self.is_player_turn or self.game_over:
            return

        buttons = self._compute_buttons()

        # 难度按钮
        for i, btn in enumerate(buttons['depth_buttons']):
            if btn.collidepoint(pos):
                self.selected_depth = self.depths[i]
                self.ai.set_depth(self.selected_depth)
                return

        # 重新开始
        if buttons['restart_btn'].collidepoint(pos):
            self.board.reset()
            self.game_over = False
            self.winner = None
            self.ai_move = None
            self.is_player_turn = True
            return

        # 悔棋（撤销两步）
        if buttons['undo_btn'].collidepoint(pos):
            if self.board.last_move is not None:
                self.board.undo_move()
            if self.board.last_move is not None:
                self.board.undo_move()
            self.game_over = False
            self.winner = None
            self.ai_move = None
            self.is_player_turn = True
            return

        if pos[0] > self.board_pixel:
            return

        col = round((pos[0] - self.padding) / self.cell_size)
        row = round((pos[1] - self.padding) / self.cell_size)

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board.make_move(row, col):
                if self.board.check_win(row, col):
                    self.game_over = True
                    self.winner = 1
                    self.is_player_turn = False
                    return
                if self.board.is_full():
                    self.game_over = True
                    self.is_player_turn = False
                    return
                self.is_player_turn = False
                self.ai_result_ready = True

    def run(self):
        def ai_think():
            self.ai_move = self.ai.get_best_move(self.board)

        running = True
        clock = pygame.time.Clock()

        while running:
            # AI落子
            if self.ai_move is not None and not self.is_player_turn and not self.game_over:
                row, col = self.ai_move
                self.board.make_move(row, col)
                if self.board.check_win(row, col):
                    self.game_over = True
                    self.winner = 2
                self.ai_move = None
                self.is_player_turn = True

            # 启动AI思考
            if self.ai_result_ready and self.ai_move is None and not self.game_over:
                self.ai_result_ready = False
                t = Thread(target=ai_think)
                t.daemon = True
                t.start()

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            # 绘制
            self.draw_board()
            self.draw_ui()
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
