import pygame

TARGET_SCREEN_WIDTH = 800
TARGET_SCREEN_HEIGHT = 800
FPS = 60

BORDER_COLOUR = "black"


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

            if number == 0:
                continue

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


def run_pygame_loop(initial_board: list[list[int]]):
    pygame.init()

    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()

    squares: list[pygame.Rect] = []
    selected: tuple[int, int] | None = None
    solved = False

    # Calculate the size of the squares and borders.
    # Bold borders should be twice as thick as plain borders
    # Plain borders should be 1/8 of the square size
    #
    # bb = bold border
    # pb = plain border
    # s  = square
    #
    # w = width
    # h = height
    #
    # bbw = 2 * pbw
    # bbh = 2 * pbh
    #
    # pbw = sw / 8
    # pbh = sh / 8
    #
    # 4bbw + 6pbw + 9sw = SCREEN_WIDTH
    # 4bbh + 6pbh + 9sh = SCREEN_HEIGHT
    #
    # Therefore:
    # 4(2 * sw / 8) + 6(sw / 8) + 9sw = SCREEN_WIDTH
    # sw + .75sw + 9sw = SCREEN_WIDTH
    # 10.75sw = SCREEN_WIDTH
    # sw = SCREEN_WIDTH / 10.75

    square_width = int(TARGET_SCREEN_WIDTH // 10.75)
    square_height = int(TARGET_SCREEN_HEIGHT // 10.75)

    plain_border_width = int(square_width // 8)
    plain_border_height = int(square_height // 8)

    bold_border_width = 2 * plain_border_width
    bold_border_height = 2 * plain_border_height

    print(f"DEBUG: {square_width = } | {square_height = }")
    print(f"DEBUG: {plain_border_width = } | {plain_border_height = }")
    print(f"DEBUG: {bold_border_width = } | {bold_border_height = }")

    # Adjust screen size according to the calculated square and border sizes.
    actual_screen_width = square_width * 9 + plain_border_width * 6 + bold_border_width * 4
    actual_screen_height = square_height * 9 + plain_border_height * 6 + bold_border_height * 4
    print(f"DEBUG: {TARGET_SCREEN_WIDTH = } | {TARGET_SCREEN_HEIGHT = }")
    print(f"DEBUG: {actual_screen_width = } | {actual_screen_height = }")
    screen = pygame.display.set_mode((actual_screen_width, actual_screen_height))

    print(f"DEBUG: {4 * bold_border_width + 6 * plain_border_width + 9 * square_width = }")
    print(f"DEBUG: {4 * bold_border_height + 6 * plain_border_height + 9 * square_height = }")

    board = [row.copy() for row in initial_board]

    screen.fill(BORDER_COLOUR)

    def get_x_of_square(col_indx: int, square_width: int, plain_border_width: int, bold_border_width: int):
        num_bold_borders = col_indx // 3
        num_plain_borders = col_indx - (num_bold_borders)

        return (
            bold_border_width * (num_bold_borders + 1)  # NB: +1 to account for the left outer border
            + plain_border_width * num_plain_borders
            + square_width * col_indx
        )

    def get_y_of_square(row_indx: int, square_height: int, plain_border_height: int, bold_border_height: int):
        num_bold_borders = row_indx // 3
        num_plain_borders = row_indx - (num_bold_borders)

        return (
            bold_border_height * (num_bold_borders + 1)  # NB: +1 to account for the top outer border
            + plain_border_height * num_plain_borders
            + square_height * row_indx
        )

    def get_square_from_coords(x: int, y: int):
        if (x < bold_border_width or x > actual_screen_width - bold_border_width) or (
            y < bold_border_height or y > actual_screen_height - bold_border_height
        ):
            print(f"DEBUG: Coords {x = } {y = } are on an outer border")
            return None

        for square in squares:
            if square.collidepoint(x, y):
                row_indx = squares.index(square) // 9
                col_indx = squares.index(square) % 9
                return row_indx, col_indx
        else:
            print(f"DEBUG: Coords {x = } {y = }are on an inner border")
            return None

    def draw_board(board: list[list[int]]):
        for row_indx in range(9):
            for col_indx in range(9):
                is_user_input = initial_board[row_indx][col_indx] == 0

                x = get_x_of_square(col_indx, square_width, plain_border_width, bold_border_width)
                y = get_y_of_square(row_indx, square_height, plain_border_height, bold_border_height)

                # Draw the square
                squares.append(
                    pygame.draw.rect(
                        screen,
                        "yellow" if selected == (row_indx, col_indx) else "white",
                        pygame.Rect(
                            x,  # start x
                            y,  # start y
                            square_width,  # width
                            square_height,  # height
                        ),
                    )
                )

                text = str(board[row_indx][col_indx]) if board[row_indx][col_indx] else ""

                # Draw the number
                font = pygame.font.Font(None, 36)  # TODO: Figure out dynamic font size based on square size
                font.set_italic(is_user_input)
                text = font.render(text, True, "blue" if is_user_input else "black")

                text_rect = text.get_rect(center=(x + square_width // 2, y + square_height // 2))
                screen.blit(text, text_rect)

            if solved:
                font = pygame.font.Font(None, 90)  # TODO: Figure out dynamic font size based on square size
                text = font.render("           Congrats!\nYou solved the Sudoku!", True, "green")
                text_rect = text.get_rect(center=(actual_screen_width // 2, actual_screen_height // 2))
                screen.blit(text, text_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("DEBUG: Quit event received...")
                running = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                square_pos = get_square_from_coords(x, y)
                if square_pos:
                    if selected == square_pos or initial_board[square_pos[0]][square_pos[1]] != 0:
                        selected = None
                    else:
                        selected = square_pos

                continue

            if event.type == pygame.KEYDOWN:
                if solved:
                    continue

                if selected and chr(event.key).isdigit():
                    row_indx, col_indx = selected
                    new_number = int(chr(event.key))

                    new_board = [row.copy() for row in board]
                    new_board[row_indx][col_indx] = new_number

                    if not is_valid_sudoku(new_board, allow_empty=True):
                        print(f"DEBUG: {new_number} is an impossible number for {row_indx=} {col_indx=}")
                        continue

                    board[row_indx][col_indx] = int(chr(event.key))
                    selected = None
                    if is_valid_sudoku(board, allow_empty=False):
                        print("DEBUG: Sudoku solved!")
                        solved = True
                        draw_board(board)
                continue

        if not solved:
            draw_board(board)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    board = [
        [0, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 0, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 0, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 0, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 0, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 0, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 0, 6, 7, 8],
    ]
    draw_sudoku_to_terminal(board)
    print(is_valid_sudoku(board, allow_empty=True))

    run_pygame_loop(board)


if __name__ == "__main__":
    main()
