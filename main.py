import random
from typing import Literal

import pygame

DIFFICULTY = "easy"  # easy, medium, hard, very hard, extreme
TARGET_SCREEN_WIDTH = 800
TARGET_SCREEN_HEIGHT = 800
FPS = 60

MIN_WIDTH = 200
MIN_HEIGHT = 200

BORDER_COLOUR = "black"

difficulty = {
    "very easy": 0.1,
    "easy": 0.3,
    "medium": 0.5,
    "hard": 0.6,
    "very hard": 0.7,
    "extreme": 0.9,
}
if DIFFICULTY not in difficulty:
    raise ValueError(f"Invalid difficulty level: {DIFFICULTY}. Choose from {', '.join(list(difficulty.keys()))}.")


def generate_random_sudoku() -> tuple[list[list[int]], list[list[int]]]:
    """Generate a valid, fully solved Sudoku board using backtracking."""

    def is_valid(board, row, col, num):
        """Check if placing a number is valid in the current board."""
        # Check the row
        if num in board[row]:
            return False

        # Check the column
        if num in [board[i][col] for i in range(9)]:
            return False

        # Check the 3x3 subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if board[i][j] == num:
                    return False

        return True

    def solve_board(board) -> list[list[int]] | Literal[False]:
        """Solve the Sudoku board using backtracking."""
        solved_board: list[list[int]] = [row.copy() for row in board]
        for row in range(9):
            for col in range(9):
                if solved_board[row][col] == 0:  # Find an empty cell
                    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                    random.shuffle(nums)
                    for num in nums:  # Try numbers 1-9
                        if is_valid(solved_board, row, col, num):
                            solved_board[row][col] = num
                            if b := solve_board(solved_board):
                                return b
                            solved_board[row][col] = 0  # Backtrack
                    return False
        return solved_board

    # Start with an empty board
    board = [[0 for _ in range(9)] for _ in range(9)]

    # Fill the board using backtracking
    solved_board = solve_board(board)
    if not solved_board:
        raise ValueError("Failed to generate a valid Sudoku board.")

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

        puzzle_board: list[list[int]] = [row.copy() for row in board]

        # Randomly shuffle cell positions
        cells = [(row, col) for row in range(9) for col in range(9)]
        random.shuffle(cells)

        num_empty_cells = 0
        for row, col in cells:
            if num_empty_cells >= max_empty_cells:
                break

            # Temporarily remove the number
            removed_value = puzzle_board[row][col]
            puzzle_board[row][col] = 0

            # Check if the board still has a unique solution
            if not has_unique_solution(puzzle_board):
                puzzle_board[row][col] = removed_value  # Undo removal
            else:
                num_empty_cells += 1

        print(f"DEBUG: {num_empty_cells = }")
        return puzzle_board

    # NB: The higher the max amount of empty cells, the more difficult the puzzle
    max_empty_cells = int((9 * 9) * difficulty[DIFFICULTY])
    print(f"DEBUG: {max_empty_cells = }")

    puzzle_board = create_puzzle(solved_board, max_empty_cells=max_empty_cells)
    return solved_board, puzzle_board


def get_subgrid(board: list[list[int]], row_indx: int, col_indx: int):
    start_row = (row_indx // 3) * 3
    end_row = start_row + 3

    start_col = (col_indx // 3) * 3
    end_col = start_col + 3

    subgrid: list[int] = []
    for i in range(start_row, end_row):
        for j in range(start_col, end_col):
            subgrid.append(board[i][j])
    return subgrid


def get_column(board: list[list[int]], col_indx: int):
        return [row[col_indx] for row in board]


def is_valid_sudoku(board: list[list[int]], *, allow_empty: bool) -> bool:
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

    squares: list[tuple[pygame.Rect, int]] = []
    selected: tuple[int, int] | None = None
    prev_selected = None
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
    actual_screen_width = TARGET_SCREEN_WIDTH
    actual_screen_height = TARGET_SCREEN_HEIGHT

    def get_square_width():
        return int(actual_screen_width // 10.75)

    def get_square_height():
        return int(actual_screen_height // 10.75)

    def get_plain_border_width():
        return int(get_square_width() // 8)

    def get_plain_border_height():
        return int(get_square_height() // 8)

    def get_bold_border_width():
        return 2 * get_plain_border_width()

    def get_bold_border_height():
        return 2 * get_plain_border_height()

    square_width = get_square_width()
    square_height = get_square_height()

    plain_border_width = get_plain_border_width()
    plain_border_height = get_plain_border_height()

    bold_border_width = get_bold_border_width()
    bold_border_height = get_bold_border_height()

    print(f"DEBUG: {square_width = } | {square_height = }")
    print(f"DEBUG: {plain_border_width = } | {plain_border_height = }")
    print(f"DEBUG: {bold_border_width = } | {bold_border_height = }")

    # Adjust screen size according to the calculated square and border sizes.
    actual_screen_width = square_width * 9 + plain_border_width * 6 + bold_border_width * 4
    actual_screen_height = square_height * 9 + plain_border_height * 6 + bold_border_height * 4
    print(f"DEBUG: {TARGET_SCREEN_WIDTH = } | {TARGET_SCREEN_HEIGHT = }")
    print(f"DEBUG: {actual_screen_width = } | {actual_screen_height = }")
    screen = pygame.display.set_mode((actual_screen_width, actual_screen_height), pygame.RESIZABLE)

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
            if square[0].collidepoint(x, y):
                row_indx = squares.index(square) // 9
                col_indx = squares.index(square) % 9
                return row_indx, col_indx
        else:
            print(f"DEBUG: Coords {x = } {y = } are on an inner border")
            return None

    def draw_board(board: list[list[int]]):
        """Draw the Sudoku board. Implemented such that only changed squares are redrawn."""
        nonlocal prev_selected
        nonlocal squares

        def draw_number(number: int, x: int, y: int, *, colour: str, italic: bool):
            text = str(number) if number else " "

            font = pygame.font.Font(None, 36)  # TODO: Figure out dynamic font size based on square size
            font.set_italic(italic)
            text = font.render(text, True, colour)

            text_rect = text.get_rect(center=(x + square_width // 2, y + square_height // 2))
            screen.blit(text, text_rect)

        for row_indx in range(9):
            for col_indx in range(9):
                is_user_input = initial_board[row_indx][col_indx] == 0

                if len(squares) > (square_indx := row_indx * 9 + col_indx):
                    # This square has been drawn before

                    if (new_number := board[row_indx][col_indx]) != squares[square_indx][1]:
                        # The number in the square has changed
                        x = squares[square_indx][0].x
                        y = squares[square_indx][0].y

                        # Draw the number
                        squares[square_indx] = (squares[square_indx][0], new_number)
                        draw_number(
                            new_number,
                            x,
                            y,
                            colour="blue",
                            italic=True,
                        )

                else:
                    # First time drawing this square

                    x = get_x_of_square(col_indx, square_width, plain_border_width, bold_border_width)
                    y = get_y_of_square(row_indx, square_height, plain_border_height, bold_border_height)

                    number = board[row_indx][col_indx]
                    squares.append(
                        (
                            pygame.draw.rect(
                                screen,
                                "white",
                                pygame.Rect(
                                    x,  # start x
                                    y,  # start y
                                    square_width,  # width
                                    square_height,  # height
                                ),
                            ),
                            number,
                        )
                    )
                    draw_number(
                        number,
                        x,
                        y,
                        colour="blue" if is_user_input else "black",
                        italic=is_user_input,
                    )

        if prev_selected != selected:
            print(f"DEBUG: {prev_selected = } {selected = }")
            prev_selected_square = squares[prev_selected[0] * 9 + prev_selected[1]] if prev_selected else None
            if prev_selected_square:
                pygame.draw.rect(screen, "white", prev_selected_square[0])
                draw_number(
                    prev_selected_square[1],
                    prev_selected_square[0].x,
                    prev_selected_square[0].y,
                    colour="blue",
                    italic=True,
                )

            currently_selected_square = squares[selected[0] * 9 + selected[1]] if selected else None
            if currently_selected_square:
                pygame.draw.rect(screen, "yellow", currently_selected_square[0])
                draw_number(
                    currently_selected_square[1],
                    currently_selected_square[0].x,
                    currently_selected_square[0].y,
                    colour="blue",
                    italic=True,
                )

            prev_selected = selected

        if solved:
            font = pygame.font.Font(None, 90)  # TODO: Figure out dynamic font size based on square size
            text = font.render("           Congrats!\nYou solved the Sudoku!", True, "green")
            text_rect = text.get_rect(center=(actual_screen_width // 2, actual_screen_height // 2))
            screen.blit(text, text_rect)

    prev_size = (actual_screen_width, actual_screen_height)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("DEBUG: Quit event received...")
                running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                print("DEBUG: Resize event received...")

                new_width = event.w
                new_height = event.h

                if new_width < MIN_WIDTH:
                    screen = pygame.display.set_mode(prev_size, pygame.RESIZABLE)
                    print(f"DEBUG: Resize event ignored (width too small). {new_width = } {new_height = }")
                    continue

                if new_height < MIN_HEIGHT:
                    screen = pygame.display.set_mode(prev_size, pygame.RESIZABLE)
                    print(f"DEBUG: Resize event ignored (height too small). {new_width = } {new_height = }")
                    continue

                if new_width > pygame.display.Info().current_w or new_height > pygame.display.Info().current_h:
                    screen = pygame.display.set_mode(prev_size, pygame.RESIZABLE)
                    print(f"DEBUG: Resize event ignored (too big). {new_width = } {new_height = }")
                    continue

                actual_screen_width = new_width
                actual_screen_height = new_height

                # TODO: "Normalize" the screen size to the match above algebraic equations
                prev_size = event.size

                screen = pygame.display.set_mode((actual_screen_width, actual_screen_height), pygame.RESIZABLE)
                squares: list[tuple[pygame.Rect, int]] = []

                print(f"DEBUG: OLD {square_width = } | {square_height = }")
                print(f"DEBUG: OLD {plain_border_width = } | {plain_border_height = }")
                print(f"DEBUG: OLD {bold_border_width = } | {bold_border_height = }")

                square_width = get_square_width()
                square_height = get_square_height()

                plain_border_width = get_plain_border_width()
                plain_border_height = get_plain_border_height()

                bold_border_width = get_bold_border_width()
                bold_border_height = get_bold_border_height()

                print(f"DEBUG: NEW {square_width = } | {square_height = }")
                print(f"DEBUG: NEW {plain_border_width = } | {plain_border_height = }")
                print(f"DEBUG: NEW {bold_border_width = } | {bold_border_height = }")

                if solved:
                    draw_board(board)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                square_pos = get_square_from_coords(x, y)
                if square_pos:
                    prev_selected = selected
                    if selected == square_pos or initial_board[square_pos[0]][square_pos[1]] != 0:
                        selected = None
                    else:
                        selected = square_pos

                continue

            if event.type == pygame.KEYDOWN:
                if solved:
                    continue

                if selected and event.key in {pygame.key.key_code(num) for num in "1234567890"}:
                    row_indx, col_indx = selected
                    new_number = int(chr(event.key))

                    new_board = [row.copy() for row in board]
                    new_board[row_indx][col_indx] = new_number

                    if not is_valid_sudoku(new_board, allow_empty=True):
                        print(f"DEBUG: {new_number} is an impossible number for {row_indx=} {col_indx=}")
                        continue

                    board[row_indx][col_indx] = new_number
                    selected = None
                    print(f"DEBUG: {board = }")
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
    print(f"DEBUG: Generating Sudoku board with difficulty: {DIFFICULTY}")
    solved_board, puzzle_board = generate_random_sudoku()

    draw_sudoku_to_terminal(solved_board)
    draw_sudoku_to_terminal(puzzle_board)

    print("DEBUG: Starting Pygame loop...")
    run_pygame_loop(puzzle_board)


if __name__ == "__main__":
    main()
