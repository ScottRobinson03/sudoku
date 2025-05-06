import random
from typing import Literal


class SudokuGenerator:
    """Class to generate Sudoku boards and puzzles."""

    difficulty_levels = {
        "very easy": 0.1,
        "easy": 0.3,
        "medium": 0.5,
        "hard": 0.6,
        "very hard": 0.7,
        "extreme": 0.9,
    }

    def __init__(self, difficulty: str):
        if difficulty not in self.difficulty_levels:
            raise ValueError(
                f"Invalid difficulty level: {difficulty}. Choose from {', '.join(self.difficulty_levels.keys())}."
            )
        self.difficulty = difficulty

    def generate_random_sudoku(self) -> tuple[list[list[int]], list[list[int]]]:
        """Generate a valid, fully solved Sudoku board and a puzzle board."""

        def is_valid(board, row, col, num):
            """Check if placing a number is valid in the current board."""
            if num in board[row]:
                return False
            if num in [board[i][col] for i in range(9)]:
                return False
            start_row, start_col = 3 * (row // 3), 3 * (col // 3)
            for i in range(start_row, start_row + 3):
                for j in range(start_col, start_col + 3):
                    if board[i][j] == num:
                        return False
            return True

        def solve_board(board) -> list[list[int]] | Literal[False]:
            """Solve the Sudoku board using backtracking."""
            solved_board = [row.copy() for row in board]
            for row in range(9):
                for col in range(9):
                    if solved_board[row][col] == 0:
                        nums = list(range(1, 10))
                        random.shuffle(nums)
                        for num in nums:
                            if is_valid(solved_board, row, col, num):
                                solved_board[row][col] = num
                                if b := solve_board(solved_board):
                                    return b
                                solved_board[row][col] = 0
                        return False
            return solved_board

        def create_puzzle(board, max_empty_cells=40) -> list[list[int]]:
            """Remove numbers from a solved Sudoku board to create a puzzle."""

            def has_unique_solution(board):
                """Check if the board has a unique solution."""
                solutions = 0

                def count_solutions(b):
                    nonlocal solutions
                    for row in range(9):
                        for col in range(9):
                            if b[row][col] == 0:
                                for num in range(1, 10):
                                    if is_valid(b, row, col, num):
                                        b[row][col] = num
                                        count_solutions(b)
                                        b[row][col] = 0
                                return
                    solutions += 1

                count_solutions([row.copy() for row in board])
                return solutions == 1

            puzzle_board = [row.copy() for row in board]
            cells = [(row, col) for row in range(9) for col in range(9)]
            random.shuffle(cells)

            num_empty_cells = 0
            for row, col in cells:
                if num_empty_cells >= max_empty_cells:
                    break
                removed_value = puzzle_board[row][col]
                puzzle_board[row][col] = 0
                if not has_unique_solution(puzzle_board):
                    puzzle_board[row][col] = removed_value
                else:
                    num_empty_cells += 1

            return puzzle_board

        board = [[0 for _ in range(9)] for _ in range(9)]
        solved_board = solve_board(board)
        if not solved_board:
            raise ValueError("Failed to generate a valid Sudoku board.")

        max_empty_cells = int((9 * 9) * self.difficulty_levels[self.difficulty])
        puzzle_board = create_puzzle(solved_board, max_empty_cells=max_empty_cells)
        return solved_board, puzzle_board
