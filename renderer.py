class SudokuRenderer:
    """Class to render Sudoku boards."""

    @staticmethod
    def _is_bold_boundary(indx: int):
        return (indx + 1) % 3 == 0 and indx + 1 != 9

    @staticmethod
    def _create_border(left, mid, right, horizontal, bold_mid, bold_cross, row_indx):
        return (
            (left if not SudokuRenderer._is_bold_boundary(row_indx) else "┣")
            + "".join(
                (
                    horizontal * 3
                    + (
                        bold_cross
                        if SudokuRenderer._is_bold_boundary(i) and SudokuRenderer._is_bold_boundary(row_indx)
                        else bold_mid
                        if SudokuRenderer._is_bold_boundary(i)
                        else mid
                    )
                )
                for i in range(8)
            )
            + horizontal * 3
            + (right if not SudokuRenderer._is_bold_boundary(row_indx) else "┫")
        )

    @staticmethod
    def draw_sudoku_to_terminal(board: list[list[int]]):
        num_rows = len(board)
        num_cols = len(board[0]) if num_rows > 0 else 0

        print(SudokuRenderer._create_border("┏", "┯", "┓", "━", "┳", "╋", 0))

        for row_indx, row in enumerate(board):
            row_line = "┃"
            for col_indx, cell in enumerate(row):
                row_line += f" {cell if cell else ' '} "
                if col_indx < num_cols - 1:
                    row_line += "┃" if SudokuRenderer._is_bold_boundary(col_indx) else "│"
            row_line += "┃"
            print(row_line)

            if row_indx != num_rows - 1:
                if SudokuRenderer._is_bold_boundary(row_indx):
                    print(SudokuRenderer._create_border("┣", "┿", "┫", "━", "╋", "╋", row_indx))
                else:
                    print(SudokuRenderer._create_border("┠", "┼", "┨", "─", "╂", "┼", row_indx))

        print(SudokuRenderer._create_border("┗", "┷", "┛", "━", "┻", "╋", len(board) - 1))
