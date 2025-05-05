def is_valid_sudoku(board: list[list[int]], *, allow_empty: bool) -> bool:
    def get_subgrid(board: list[list[int]], row_indx: int, col_indx: int):
        start_row = (row_indx // 3) * 3
        end_row = start_row + 3

        start_col = (col_indx // 3) * 3
        end_col = start_col + 3

        subgrid = []
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                subgrid.append(board[i][j])
        return subgrid

    def get_column(board: list[list[int]], col_indx: int):
        return [row[col_indx] for row in board]

    for row_indx, row in enumerate(board):
        if row_indx > 8:
            # Too many rows
            return False

        for col_indx, number in enumerate(row):
            if col_indx > 8:
                # Too many columns
                return False

            if number < (0 if allow_empty else 1) or number > 9:
                # Invalid number
                return False

            if row.count(number) > 1:
                # Duplicate number in row
                return False

            if get_column(board, col_indx).count(number) > 1:
                # Duplicate number in column
                return False

            if get_subgrid(board, row_indx, col_indx).count(number) > 1:
                # Duplicate number in subgrid (3x3 grid)
                return False

    return True


def draw_sudoku_to_terminal(board: list[list[int]]):
    num_rows = len(board)
    num_cols = len(board[0]) if num_rows > 0 else 0

    # Helper function to determine if a bold boundary is needed
    def is_bold_boundary(indx, size):
        return (indx + 1) % 3 == 0 and indx + 1 != size

    # Helper function to create a border line
    def create_border(left, mid, right, horizontal, bold_mid, bold_cross, row_indx):
        return (
            (left if not is_bold_boundary(row_indx, num_rows) else "┣")
            + "".join(
                (
                    horizontal * 3
                    + (
                        bold_cross
                        if is_bold_boundary(i, num_cols) and is_bold_boundary(row_indx, num_rows)
                        else bold_mid
                        if is_bold_boundary(i, num_cols)
                        else mid
                    )
                )
                for i in range(num_cols - 1)
            )
            + horizontal * 3
            + (right if not is_bold_boundary(row_indx, num_rows) else "┫")
        )

    print(create_border("┏", "┯", "┓", "━", "┳", "╋", 0))

    for row_indx, row in enumerate(board):
        # Print row content with dynamic vertical separators
        row_line = "┃"
        for col_indx, cell in enumerate(row):
            row_line += f" {cell if cell else ' '} "
            if col_indx < num_cols - 1:
                # Use `┃` if the column is a 3x3 boundary
                if is_bold_boundary(col_indx, num_cols):
                    row_line += "┃"
                # Otherwise, use `│`
                else:
                    row_line += "│"
        row_line += "┃"
        print(row_line)

        if row_indx != num_rows - 1:
            if is_bold_boundary(row_indx, num_rows):
                print(create_border("┣", "┿", "┫", "━", "╋", "╋", row_indx))
            else:
                print(create_border("┠", "┼", "┨", "─", "╂", "┼", row_indx))

    print(create_border("┗", "┷", "┛", "━", "┻", "╋", row_indx))


def main():
    board = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    draw_sudoku_to_terminal(board)
    print(is_valid_sudoku(board, allow_empty=False))

if __name__ == "__main__":
    main()
