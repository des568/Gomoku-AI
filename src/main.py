from board import Board
from ai import AI
from ui import UI

def main():
    board = Board()
    ai = AI(depth=4)
    ui = UI(board, ai)
    ui.run()

if __name__ == "__main__":
    main()