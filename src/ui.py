import pygame
import sys

class UI:
    def __init__(self, board, ai):
        pygame.init()
        self.board = board
        self.ai = ai
        self.screen_width = 650
        self.screen_height = 550
        self.cell_size = 35
        self.padding = 30
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Gomoku-AI")
        
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BOARD_COLOR = (200, 160, 100)
        self.HIGHLIGHT_COLOR = (255, 0, 0)
        self.TEXT_COLOR = (50, 50, 50)
        
        # 尝试加载支持中文的字体
        self.font = self._get_font(24)
        self.small_font = self._get_font(18)
        
        self.selected_depth = 4
        self.depths = [2, 4, 6]
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        self.ai_move = None
    
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
        
        for i in range(1, 15):
            x = self.padding + i * self.cell_size
            pygame.draw.line(self.screen, self.BLACK, (x, self.padding), (x, self.padding + 14 * self.cell_size), 1)
            pygame.draw.line(self.screen, self.BLACK, (self.padding, x), (self.padding + 14 * self.cell_size, x), 1)
        
        for i in [3, 7, 11]:
            x = self.padding + i * self.cell_size
            pygame.draw.circle(self.screen, self.BLACK, (x, x), 4, 0)
        
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.board[row][col] != Board.EMPTY:
                    x = self.padding + col * self.cell_size
                    y = self.padding + row * self.cell_size
                    color = self.BLACK if self.board.board[row][col] == Board.BLACK else self.WHITE
                    pygame.draw.circle(self.screen, color, (x, y), 15, 0)
                    
                    if color == self.WHITE:
                        pygame.draw.circle(self.screen, self.BLACK, (x, y), 15, 1)
        
        if self.ai_move and not self.game_over:
            x = self.padding + self.ai_move[1] * self.cell_size
            y = self.padding + self.ai_move[0] * self.cell_size
            pygame.draw.circle(self.screen, self.HIGHLIGHT_COLOR, (x, y), 8, 2)
    
    def draw_ui(self):
        start_x = self.padding + 15 * self.cell_size + 20
        
        depth_text = self.font.render("难度:", True, self.TEXT_COLOR)
        self.screen.blit(depth_text, (start_x, 30))
        
        for i, depth in enumerate(self.depths):
            y = 60 + i * 30
            rect = pygame.Rect(start_x, y, 60, 25)
            color = (100, 150, 200) if self.selected_depth == depth else (200, 200, 200)
            pygame.draw.rect(self.screen, color, rect)
            
            text = self.small_font.render(f"{depth}层", True, self.TEXT_COLOR)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        restart_btn = pygame.Rect(start_x, 150, 80, 30)
        pygame.draw.rect(self.screen, (100, 200, 100), restart_btn)
        restart_text = self.font.render("重新开始", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=restart_btn.center)
        self.screen.blit(restart_text, restart_rect)
        
        undo_btn = pygame.Rect(start_x, 190, 80, 30)
        pygame.draw.rect(self.screen, (200, 100, 100), undo_btn)
        undo_text = self.font.render("悔棋", True, self.WHITE)
        undo_rect = undo_text.get_rect(center=undo_btn.center)
        self.screen.blit(undo_text, undo_rect)
        
        if self.ai_thinking:
            thinking_text = self.font.render("AI 思考中...", True, (255, 100, 100))
            self.screen.blit(thinking_text, (start_x, 240))
        
        if self.game_over:
            winner_text = self.font.render(f"{'黑棋' if self.winner == Board.BLACK else '白棋'}获胜!", True, (255, 0, 0))
            self.screen.blit(winner_text, (start_x, 280))
        
        current_text = self.font.render(f"当前回合: {'黑棋' if self.board.current_player == Board.BLACK else '白棋'}", True, self.TEXT_COLOR)
        self.screen.blit(current_text, (start_x, 320))
        
        return {
            'depth_buttons': [pygame.Rect(start_x, 60 + i * 30, 60, 25) for i in range(3)],
            'restart_btn': restart_btn,
            'undo_btn': undo_btn
        }
    
    def handle_click(self, pos):
        buttons = self.draw_ui()
        
        for i, btn in enumerate(buttons['depth_buttons']):
            if btn.collidepoint(pos):
                self.selected_depth = self.depths[i]
                self.ai.set_depth(self.selected_depth)
                return
        
        if buttons['restart_btn'].collidepoint(pos):
            self.board.reset()
            self.game_over = False
            self.winner = None
            self.ai_move = None
            return
        
        if buttons['undo_btn'].collidepoint(pos):
            self.board.undo_move()
            self.board.undo_move()
            self.game_over = False
            self.winner = None
            self.ai_move = None
            return
        
        x, y = pos
        col = round((x - self.padding) / self.cell_size)
        row = round((y - self.padding) / self.cell_size)
        
        if 0 <= row < self.board.size and 0 <= col < self.board.size:
            if self.board.make_move(row, col):
                self.ai_move = None
                
                if self.board.check_win(row, col):
                    self.game_over = True
                    self.winner = Board.BLACK
                    return
                
                if self.board.is_full():
                    self.game_over = True
                    return
                
                self.ai_thinking = True
                pygame.display.flip()
                
                self.ai_move = self.ai.get_best_move(self.board)
                
                if self.ai_move:
                    self.board.make_move(self.ai_move[0], self.ai_move[1])
                    
                    if self.board.check_win(self.ai_move[0], self.ai_move[1]):
                        self.game_over = True
                        self.winner = Board.WHITE
                
                self.ai_thinking = False
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_over:
                        self.handle_click(event.pos)
            
            self.draw_board()
            self.draw_ui()
            pygame.display.flip()
        
        pygame.quit()

from board import Board