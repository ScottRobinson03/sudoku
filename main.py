from game import SudokuGame

DIFFICULTY = "easy"

TARGET_SCREEN_WIDTH = 900
TARGET_SCREEN_HEIGHT = 675

if __name__ == "__main__":
    game = SudokuGame(DIFFICULTY, TARGET_SCREEN_WIDTH, TARGET_SCREEN_HEIGHT)
    game.play()
