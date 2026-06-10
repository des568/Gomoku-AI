import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from board import Board
from ai import AI
from ui import UI

def main():
    board = Board()
    ai = AI(depth=2)
    ui = UI(board, ai)
    ui.run()

if __name__ == "__main__":
    main()