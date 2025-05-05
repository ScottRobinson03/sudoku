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


if __name__ == "__main__":
    main()
