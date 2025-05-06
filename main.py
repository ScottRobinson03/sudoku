from game import SudokuGame

DIFFICULTY = "easy"

TARGET_SCREEN_WIDTH = 800
TARGET_SCREEN_HEIGHT = 600

if __name__ == "__main__":
    game = SudokuGame(DIFFICULTY, TARGET_SCREEN_WIDTH, TARGET_SCREEN_HEIGHT)
    game.play()
