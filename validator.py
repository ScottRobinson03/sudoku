class SudokuValidator:
    """Class to validate Sudoku boards."""

    @staticmethod
    def get_subgrid(board: list[list[int]], row_indx: int, col_indx: int):
        start_row = (row_indx // 3) * 3
        end_row = start_row + 3
        start_col = (col_indx // 3) * 3
        end_col = start_col + 3
        return [board[i][j] for i in range(start_row, end_row) for j in range(start_col, end_col)]

    @staticmethod
    def get_column(board: list[list[int]], col_indx: int):
        return [row[col_indx] for row in board]

    @staticmethod
    def is_valid_sudoku(board: list[list[int]], *, allow_empty: bool) -> bool:
        for row_indx, row in enumerate(board):
            if row_indx > 8:
                return False
            for col_indx, number in enumerate(row):
                if col_indx > 8:
                    return False
                if number < (0 if allow_empty else 1) or number > 9:
                    return False
                if number == 0:
                    continue
                if row.count(number) > 1:
                    return False
                if SudokuValidator.get_column(board, col_indx).count(number) > 1:
                    return False
                if SudokuValidator.get_subgrid(board, row_indx, col_indx).count(number) > 1:
                    return False
        return True

    @staticmethod
    def get_incorrect_squares(solved_board: list[list[int]], puzzle_board: list[list[int]]) -> set[tuple[int, int]]:
        incorrect_squares: set[tuple[int, int]] = set()
        for row_indx, row in enumerate(puzzle_board):
            for col_indx, number in enumerate(row):
                if number != 0 and number != solved_board[row_indx][col_indx]:
                    incorrect_squares.add((row_indx, col_indx))
        return incorrect_squares
