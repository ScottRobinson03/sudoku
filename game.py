import pygame

from generator import SudokuGenerator
from renderer import SudokuRenderer
from validator import SudokuValidator

MIN_WIDTH = 200
MIN_HEIGHT = 200
FPS = 60


class SudokuGame:
    """Main Sudoku game class."""

    def __init__(self, difficulty: str, target_screen_width: int, target_screen_height: int):
        self.generator = SudokuGenerator(difficulty)
        self.solved_board, self.initial_board = self.generator.generate_random_sudoku()

        SudokuRenderer.draw_sudoku_to_terminal(self.solved_board)
        SudokuRenderer.draw_sudoku_to_terminal(self.initial_board)

        self.board = [row.copy() for row in self.initial_board]
        self.prev_selected: tuple[int, int] | None = None
        self.selected: tuple[int, int] | None = None
        self.solved = False
        self.squares = []

        self.incorrect_squares_indexes: set[tuple[int, int]] = set()
        self.correct_squares_indexes: set[tuple[int, int]] = set()
        self.unsure_squares_indexes: set[tuple[int, int]] = set()

        self.actual_screen_width = target_screen_width
        self.actual_screen_height = target_screen_height

        self.calculate_dimensions()

        pygame.init()
        pygame.display.set_caption("Sudoku")

        self.clock = pygame.time.Clock()

    def calculate_dimensions(self):
        """Calculate square and border dimensions dynamically."""
        # Bold borders should be twice as thick as plain borders
        # Plain borders should be 1/8 of the square size
        #
        # btn = button
        # bb = bold border
        # pb = plain border
        # s  = square
        #
        # w = width
        # h = height
        #
        # btnw = 3sw + 2pbw
        # btnh = sh
        #
        # bbw = 2 * pbw
        # bbh = 2 * pbh
        #
        # pbw = sw / 8
        # pbh = sh / 8
        #
        # 4bbw + 6pbw + 9sw = SCREEN_WIDTH
        # 5bbh + 6pbh + 9sh + btnh  = SCREEN_HEIGHT
        #
        # Therefore:
        # 4(2 * sw / 8) + 6(sw / 8) + 9sw = SCREEN_WIDTH
        # sw + .75sw + 9sw = SCREEN_WIDTH
        # 10.75sw = SCREEN_WIDTH
        # sw = SCREEN_WIDTH / 10.75
        #
        # 5(2 * sh / 8) + 6(sh / 8) + 10sh = SCREEN_HEIGHT
        # 1.25sh + .75sh + 10sh = SCREEN_HEIGHT
        # 12sh = SCREEN_HEIGHT
        # sh = SCREEN_HEIGHT / 12

        self.square_width = int(self.actual_screen_width // 10.75)
        self.square_height = int(self.actual_screen_height // 12)

        self.plain_border_width = int(self.square_width // 8)
        self.plain_border_height = int(self.square_height // 8)

        self.btn_width = 3 * self.square_width + 2 * self.plain_border_width
        self.btn_height = self.square_height

        self.bold_border_width = 2 * self.plain_border_width
        self.bold_border_height = 2 * self.plain_border_height

        # Adjust screen size based on calculated dimensions
        self.actual_screen_width = self.square_width * 9 + self.plain_border_width * 6 + self.bold_border_width * 4
        self.actual_screen_height = (
            self.square_height * 9 + self.plain_border_height * 6 + self.bold_border_height * 5 + self.btn_height
        )
        self.screen = pygame.display.set_mode((self.actual_screen_width, self.actual_screen_height), pygame.RESIZABLE)

    def draw_board(self):
        """Draw the Sudoku board on the screen."""
        for row_indx in range(9):
            for col_indx in range(9):
                is_user_input = self.initial_board[row_indx][col_indx] == 0

                if len(self.squares) > (square_indx := row_indx * 9 + col_indx):
                    # This square has been drawn before

                    if (new_number := self.board[row_indx][col_indx]) != self.squares[square_indx][1]:
                        # The number in the square has changed
                        x = self.squares[square_indx][0].x
                        y = self.squares[square_indx][0].y

                        # Draw the number
                        self.squares[square_indx] = (self.squares[square_indx][0], new_number)
                        self.draw_number(
                            new_number,
                            x,
                            y,
                            colour="blue",
                            italic=True,
                        )

                else:
                    # First time drawing this square

                    x = self.get_x_of_square(
                        col_indx  # , self.square_width, self.plain_border_width, self.bold_border_width
                    )
                    y = self.get_y_of_square(
                        row_indx  # , self.square_height, self.plain_border_height, self.bold_border_height
                    )

                    number = self.board[row_indx][col_indx]
                    self.squares.append(
                        (
                            pygame.draw.rect(
                                self.screen,
                                "white",
                                pygame.Rect(
                                    x,  # start x
                                    y,  # start y
                                    self.square_width,  # width
                                    self.square_height,  # height
                                ),
                            ),
                            number,
                        )
                    )
                    self.draw_number(
                        number,
                        x,
                        y,
                        colour="blue" if is_user_input else "black",
                        italic=is_user_input,
                    )

        if self.prev_selected != self.selected:
            print(f"DEBUG: {self.prev_selected = } {self.selected = }")
            prev_selected_square = (
                self.squares[self.prev_selected[0] * 9 + self.prev_selected[1]] if self.prev_selected else None
            )
            if prev_selected_square:
                pygame.draw.rect(self.screen, "white", prev_selected_square[0])
                self.draw_number(
                    prev_selected_square[1],
                    prev_selected_square[0].x,
                    prev_selected_square[0].y,
                    colour="blue",
                    italic=True,
                )

            currently_selected_square = self.squares[self.selected[0] * 9 + self.selected[1]] if self.selected else None
            if currently_selected_square:
                pygame.draw.rect(self.screen, "yellow", currently_selected_square[0])
                self.draw_number(
                    currently_selected_square[1],
                    currently_selected_square[0].x,
                    currently_selected_square[0].y,
                    colour="blue",
                    italic=True,
                )

            self.prev_selected = self.selected

        if self.solved:
            font = pygame.font.Font(None, 90)  # TODO: Figure out dynamic font size based on square size
            text = font.render("           Congrats!\nYou solved the Sudoku!", True, "green")
            text_rect = text.get_rect(center=(self.actual_screen_width // 2, self.actual_screen_height // 2))
            self.screen.blit(text, text_rect)

    def draw_buttons(self):
        """Draw the buttons on the screen."""

        def draw_verify_button():
            verify_btn_x = self.get_x_of_square(0)
            verify_btn_y = self.get_y_of_square(9)

            print("DEBUG: verify_btn coords", verify_btn_x, verify_btn_y)

            pygame.draw.rect(
                self.screen,
                "green",
                pygame.Rect(
                    verify_btn_x,
                    verify_btn_y,
                    self.btn_width,
                    self.btn_height,
                ),
            )
            verify_btn_text = "Verify"
            font = pygame.font.Font(None, 36)  # TODO: Figure out dynamic font size based on square size
            text = font.render(verify_btn_text, True, "black")
            text_rect = text.get_rect(center=(verify_btn_x + self.btn_width // 2, verify_btn_y + self.btn_height // 2))
            self.screen.blit(text, text_rect)

        def draw_solve_button():
            solve_btn_x = self.get_x_of_square(3)
            solve_btn_y = self.get_y_of_square(9)

            print("DEBUG: solve_btn coords", solve_btn_x, solve_btn_y)

            pygame.draw.rect(
                self.screen,
                "lightblue",
                pygame.Rect(
                    solve_btn_x,
                    solve_btn_y,
                    self.btn_width,
                    self.btn_height,
                ),
            )
            solve_btn_text = "Solve"
            font = pygame.font.Font(None, 36)
            text = font.render(solve_btn_text, True, "black")
            text_rect = text.get_rect(center=(solve_btn_x + self.btn_width // 2, solve_btn_y + self.btn_height // 2))
            self.screen.blit(text, text_rect)

        def draw_hint_button():
            hint_btn_x = self.get_x_of_square(6)
            hint_btn_y = self.get_y_of_square(9)

            print("DEBUG: hint_btn coords", hint_btn_x, hint_btn_y)

            pygame.draw.rect(
                self.screen,
                "orange",
                pygame.Rect(
                    hint_btn_x,
                    hint_btn_y,
                    self.btn_width,
                    self.btn_height,
                ),
            )
            hint_btn_text = "Hint"
            font = pygame.font.Font(None, 36)
            text = font.render(hint_btn_text, True, "black")
            text_rect = text.get_rect(center=(hint_btn_x + self.btn_width // 2, hint_btn_y + self.btn_height // 2))
            self.screen.blit(text, text_rect)

        draw_verify_button()
        draw_solve_button()
        draw_hint_button()

    def draw_number(self, number, x, y, colour="black", italic=False):
        text = str(number) if number else " "

        font = pygame.font.Font(None, 36)  # TODO: Figure out dynamic font size based on square size
        font.set_italic(italic)
        text = font.render(text, True, colour)

        text_rect = text.get_rect(center=(x + self.square_width // 2, y + self.square_height // 2))
        self.screen.blit(text, text_rect)

    def get_x_of_square(self, col_indx: int):
        """Calculate the x-coordinate of a square."""
        num_bold_borders = col_indx // 3
        num_plain_borders = col_indx - num_bold_borders
        return (
            self.bold_border_width * (num_bold_borders + 1)
            + self.plain_border_width * num_plain_borders
            + self.square_width * col_indx
        )

    def get_y_of_square(self, row_indx: int):
        """Calculate the y-coordinate of a square."""
        num_bold_borders = row_indx // 3
        num_plain_borders = row_indx - num_bold_borders
        return (
            self.bold_border_height * (num_bold_borders + 1)
            + self.plain_border_height * num_plain_borders
            + self.square_height * row_indx
        )

    def handle_mouse_click(self, pos: tuple[int, int]):
        """Handle mouse click events to select a square."""

        def handle_verify_button_clicked():
            if self.solved:
                return

            print("DEBUG: Verify button clicked")

            incorrect_square_indexes = SudokuValidator.get_incorrect_squares(self.solved_board, self.board)
            for unsure_square_indx in self.unsure_squares_indexes.copy():
                row_indx, col_indx = unsure_square_indx

                square_indx = row_indx * 9 + col_indx
                square_rect, square_number = self.squares[square_indx]

                if unsure_square_indx in incorrect_square_indexes:
                    colour = "red"
                    self.incorrect_squares_indexes.add(unsure_square_indx)
                else:
                    colour = "green"  # TODO: Use a colour with better constrast on white background
                    self.correct_squares_indexes.add(unsure_square_indx)

                self.unsure_squares_indexes.discard(unsure_square_indx)

                pygame.draw.rect(self.screen, "white", square_rect)
                self.draw_number(
                    square_number,
                    square_rect.x,
                    square_rect.y,
                    colour=colour,
                    italic=False,
                )

        def handle_solve_button_clicked():
            if self.solved:
                return

            print("DEBUG: Solve button clicked")

            for row_indx, row in enumerate(self.solved_board):
                for col_indx, correct_number in enumerate(row):
                    square_indx = row_indx * 9 + col_indx
                    square_rect, number_in_square = self.squares[square_indx]

                    colour = (
                        # was pre-solved
                        "black"
                        if self.initial_board[row_indx][col_indx] != 0
                        # entered correct number
                        else "green"
                        if number_in_square == correct_number
                        # didn't enter a number
                        else "grey"
                        if number_in_square == 0
                        # entered wrong number
                        else "red"
                    )

                    self.board[row_indx][col_indx] = correct_number
                    self.squares[square_indx] = (square_rect, correct_number)

                    self.correct_squares_indexes.add((row_indx, col_indx))
                    self.unsure_squares_indexes.discard((row_indx, col_indx))
                    self.incorrect_squares_indexes.discard((row_indx, col_indx))

                    pygame.draw.rect(self.screen, "white", square_rect)
                    self.draw_number(
                        correct_number,
                        square_rect.x,
                        square_rect.y,
                        colour=colour,
                        italic=False,
                    )
                    self.solved = True

        x, y = pos

        # TODO: Possibly refactor to utilise `self.squares` instead of this for loop? Maybe refactor into get_cell_indexes_at_pos()?
        for row_indx in range(10):  # NB: 9 rows for squares + 1 row for buttons
            for col_indx in range(9):
                rect = pygame.Rect(
                    self.get_x_of_square(col_indx),
                    self.get_y_of_square(row_indx),
                    self.square_width,
                    self.square_height,
                )
                if rect.collidepoint(x, y):
                    if row_indx == 9:
                        # Clicked on the button row
                        # BUG: Currently the click detection doesn't handle clicking the button on what would-be a square column border
                        self.selected = None

                        # TODO: Make button detection more dynamic (e.g. `self.buttons` list)

                        if col_indx in range(3):
                            handle_verify_button_clicked()

                        elif col_indx in range(3, 6):
                            handle_solve_button_clicked()

                        elif col_indx in range(6, 9):
                            print("DEBUG: Hint button clicked")
                        else:
                            print("WARNING: Invalid column clicked on button row???")

                        return

                    # Clicked on a square
                    if (
                        # Only allow selecting initially empty cells that aren't already known to be correct
                        self.initial_board[row_indx][col_indx] == 0
                        and (row_indx, col_indx) not in self.correct_squares_indexes
                    ):
                        if self.selected == (row_indx, col_indx):
                            self.selected = None
                        else:
                            self.selected = (row_indx, col_indx)
                    else:
                        self.selected = None
                    return

    def handle_key_press(self, key):
        """Handle key press events to input numbers."""
        if self.solved:
            return

        if self.selected and key in {pygame.key.key_code(num) for num in "1234567890"}:
            row_indx, col_indx = self.selected

            new_number = int(chr(key))

            new_board = [row.copy() for row in self.board]
            new_board[row_indx][col_indx] = new_number

            if not SudokuValidator.is_valid_sudoku(new_board, allow_empty=True):
                print(f"DEBUG: {new_number} is an impossible number for {row_indx=} {col_indx=}")
                return

            self.board[row_indx][col_indx] = new_number

            self.unsure_squares_indexes.add(self.selected)
            self.incorrect_squares_indexes.discard(self.selected)
            self.selected = None

            print(f"DEBUG: {self.board = }")
            if SudokuValidator.is_valid_sudoku(self.board, allow_empty=False):
                print("DEBUG: Sudoku solved!")
                self.solved = True
                self.draw_board()

    def update_screen_size(self, new_width, new_height):
        """Handle screen resizing events."""
        if new_width < MIN_WIDTH:
            self.screen = pygame.display.set_mode(self.prev_size, pygame.RESIZABLE)
            print(f"DEBUG: Resize event ignored (width too small). {new_width = } {new_height = }")
            return

        if new_height < MIN_HEIGHT:
            self.screen = pygame.display.set_mode(self.prev_size, pygame.RESIZABLE)
            print(f"DEBUG: Resize event ignored (height too small). {new_width = } {new_height = }")
            return

        if new_width > pygame.display.Info().current_w or new_height > pygame.display.Info().current_h:
            self.screen = pygame.display.set_mode(self.prev_size, pygame.RESIZABLE)
            print(f"DEBUG: Resize event ignored (too big). {new_width = } {new_height = }")
            return

        self.prev_size = (new_width, new_height)

        self.squares: list[tuple[pygame.Rect, int]] = []

        self.actual_screen_width = new_width
        self.actual_screen_height = new_height
        self.calculate_dimensions()

        self.draw_buttons()

        if self.solved:
            self.draw_board()

    def game_loop(self):
        """Main game loop."""
        self.draw_buttons()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.MOUSEBUTTONDOWN:
                    print("DEBUG: CLICK")
                    self.handle_mouse_click(event.pos)
                    continue

                if event.type == pygame.KEYDOWN:
                    self.handle_key_press(event.key)
                    continue

                if event.type == pygame.VIDEORESIZE:
                    self.update_screen_size(event.w, event.h)
                    continue

            if not self.solved:
                self.draw_board()

            pygame.display.flip()
            self.clock.tick(FPS)

    def play(self):
        """Start the game."""
        self.game_loop()
        pygame.quit()
