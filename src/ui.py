import pygame
import sys

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
        self.HIGHLIGHT_COLOR = (255, 0, 0)
        self.TEXT_COLOR = (50, 50, 50)
        
        # 尝试加载支持中文的字体
        self.font = self._get_font(22)
        self.small_font = self._get_font(16)
        
        self.selected_depth = 4
        self.depths = [2, 4, 6]
        self.game_over = False
        self.winner = None
        self.ai_move = None  # AI的落子位置
        self.is_player_turn = True  # 是否是玩家回合
        self.ai_result_ready = False  # AI计算是否完成
    
    def _get_font(self, size):
        """获取支持中文的字体"""
        fonts_to_try = [
            "C:/Windows/Fonts/simhei.ttf",      # 黑体
            "C:/Windows/Fonts/msyh.ttc",         # 微软雅黑
            "C:/Windows/Fonts/simsun.ttc",       # 宋体
            "Arial",
            None  # 默认字体作为最后备选
        ]
        
        for font_path in fonts_to_try:
            try:
                if font_path is None:
                    return pygame.font.Font(None, size)
                return pygame.font.Font(font_path, size)
            except:
                continue
        
        return pygame.font.Font(None, size)
    
    def draw_board(self):
        self.screen.fill(self.BOARD_COLOR)
        
        # 绘制棋盘线
        line_end = self.padding + (self.board_size - 1) * self.cell_size
        for i in range(self.board_size):
            x = self.padding + i * self.cell_size
            pygame.draw.line(self.screen, self.BLACK, (x, self.padding), (x, line_end), 1)
            pygame.draw.line(self.screen, self.BLACK, (self.padding, x), (line_end, x), 1)
        
        # 绘制星位（天元和四个角星）
        for i in [3, 7, 11]:
            x = self.padding + i * self.cell_size
            for j in [3, 7, 11]:
                y = self.padding + j * self.cell_size
                pygame.draw.circle(self.screen, self.BLACK, (x, y), 4, 0)
        
        # 绘制棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board.board[row][col] != 0:
                    x = self.padding + col * self.cell_size
                    y = self.padding + row * self.cell_size
                    color = self.BLACK if self.board.board[row][col] == 1 else self.WHITE
                    pygame.draw.circle(self.screen, color, (x, y), self.cell_size // 2 - 2, 0)
                    
                    if color == self.WHITE:
                        pygame.draw.circle(self.screen, self.BLACK, (x, y), self.cell_size // 2 - 2, 1)
        
        # 绘制AI建议位置（半透明绿色圆圈）
        if self.ai_move and not self.game_over:
            x = self.padding + self.ai_move[1] * self.cell_size
            y = self.padding + self.ai_move[0] * self.cell_size
            # 绘制半透明圆圈
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 255, 0, 100), (self.cell_size // 2, self.cell_size // 2), self.cell_size // 2 - 2, 2)
            self.screen.blit(s, (x - self.cell_size // 2, y - self.cell_size // 2))
    
    def draw_ui(self):
        # 右侧面板起始位置
        panel_x = self.board_pixel + 10
        panel_y = 30
        panel_width = 180
        
        # 绘制面板背景
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
        
        # 难度选择
        difficulty_label = self.small_font.render("难度:", True, self.TEXT_COLOR)
        self.screen.blit(difficulty_label, (current_x, panel_y))
        panel_y += 22
        
        for i, depth in enumerate(self.depths):
            btn_rect = pygame.Rect(current_x, panel_y, 55, 25)
            is_selected = self.selected_depth == depth
            color = (70, 130, 180) if is_selected else (220, 220, 220)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)
            
            depth_names = {2: "简单", 4: "中等", 6: "困难"}
            text = self.small_font.render(f"{depth_names[depth]}", True, self.WHITE if is_selected else self.TEXT_COLOR)
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)
            panel_y += 30
        
        panel_y += 15
        
        # 按钮
        btn_width = 80
        btn_height = 32
        
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
        
        return {
            'depth_buttons': [pygame.Rect(current_x, 77 + i * 30, 55, 25) for i in range(3)],
            'restart_btn': restart_btn,
            'undo_btn': undo_btn
        }
    
    def handle_click(self, pos):
        # 只有玩家回合才能落子
        if not self.is_player_turn or self.game_over:
            return
        
        buttons = self.draw_ui()
        
        # 检查难度按钮
        for i, btn in enumerate(buttons['depth_buttons']):
            if btn.collidepoint(pos):
                self.selected_depth = self.depths[i]
                self.ai.set_depth(self.selected_depth)
                return
        
        # 检查重新开始按钮
        if buttons['restart_btn'].collidepoint(pos):
            self.board.reset()
            self.game_over = False
            self.winner = None
            self.ai_move = None
            self.is_player_turn = True
            return
        
        # 检查悔棋按钮
        if buttons['undo_btn'].collidepoint(pos):
            # 撤销两步（玩家和AI各一步）
            if self.board.last_move is not None:
                self.board.undo_move()
                self.board.undo_move()
            self.game_over = False
            self.winner = None
            self.ai_move = None
            self.is_player_turn = True
            return
        
        # 检查是否点击在棋盘内
        if pos[0] > self.board_pixel:
            return  # 点击在右侧面板，不处理
        
        col = round((pos[0] - self.padding) / self.cell_size)
        row = round((pos[1] - self.padding) / self.cell_size)
        
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board.make_move(row, col):
                # 检查玩家是否获胜
                if self.board.check_win(row, col):
                    self.game_over = True
                    self.winner = 1  # 黑棋
                    self.is_player_turn = False
                    return
                
                # 检查是否平局
                if self.board.is_full():
                    self.game_over = True
                    self.is_player_turn = False
                    return
                
                # 玩家落子完成，切换到AI回合
                self.is_player_turn = False
                self.ai_result_ready = True  # 标记AI可以开始思考
    
    def run(self):
        from threading import Thread
        
        def ai_think():
            """AI思考线程"""
            self.ai_move = self.ai.get_best_move(self.board)
        
        running = True
        while running:
            # ===== 核心逻辑：处理AI落子 =====
            # 只有当AI思考完成（ai_move不为空）且不是玩家回合时才执行
            if self.ai_move is not None and not self.is_player_turn and not self.game_over:
                # 执行AI落子
                row, col = self.ai_move
                self.board.make_move(row, col)
                
                # 检查AI是否获胜
                if self.board.check_win(row, col):
                    self.game_over = True
                    self.winner = 2  # 白棋
                
                # 重置状态，切换回玩家回合
                self.ai_move = None
                self.is_player_turn = True
            
            # 启动AI思考线程
            if self.ai_result_ready and self.ai_move is None and not self.game_over:
                self.ai_result_ready = False
                t = Thread(target=ai_think)
                t.daemon = True
                t.start()
            
            # ===== 处理用户输入 =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # ===== 绘制界面 =====
            self.draw_board()
            self.draw_ui()
            pygame.display.flip()
            
            # 控制帧率，避免CPU占用过高
            pygame.time.delay(30)
        
        pygame.quit()