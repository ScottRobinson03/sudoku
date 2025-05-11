from typing import Callable, TypedDict
import pygame

from generator import SudokuGenerator
from renderer import SudokuRenderer
from validator import SudokuValidator

MIN_WIDTH = 200
MIN_HEIGHT = 200
FPS = 60

CORRECT_COLOUR = "chartreuse3"
WRONG_COLOUR = "red"
HINT_COLOUR = "orange"
SOLVED_COLOUR = "grey"
INPUT_COLOUR = "blue"


class Button(TypedDict):
    """Button class for the Sudoku game."""

    name: str
    colour: str
    on_click: Callable
    rect: pygame.Rect | None


class SudokuGame:
    """Main Sudoku game class."""

    def __init__(self, difficulty: str, target_screen_width: int, target_screen_height: int):
        self.difficulty = difficulty
        self.target_screen_width = target_screen_width
        self.target_screen_height = target_screen_height

        pygame.init()
        pygame.display.set_caption("Sudoku")

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

        self.prev_size = (self.actual_screen_width, self.actual_screen_height)

        self.square_width = int(self.actual_screen_width // 10.75)
        self.square_height = int(self.actual_screen_height // 12)

        self.plain_border_width = int(self.square_width // 8)
        self.plain_border_height = int(self.square_height // 8)

        self.bold_border_width = 2 * self.plain_border_width
        self.bold_border_height = 2 * self.plain_border_height

        # Adjust screen size based on calculated dimensions
        self.actual_screen_width = self.square_width * 9 + self.plain_border_width * 6 + self.bold_border_width * 4

        self.btn_height = self.square_height
        num_btns = len(self.buttons)
        # n = number of buttons
        # width of all buttons with separates = actual_screen_width
        # n(btn_width) + (n + 1)(bold_border_width) = actual_screen_width
        # btn_width = (actual_screen_width - (n + 1)(bold_border_width)) / n
        self.btn_width = (self.actual_screen_width - (num_btns + 1) * self.bold_border_width) / num_btns

        self.actual_screen_height = (
            self.square_height * 9 + self.plain_border_height * 6 + self.bold_border_height * 5 + self.btn_height
        )
        self.screen = pygame.display.set_mode((self.actual_screen_width, self.actual_screen_height), pygame.RESIZABLE)

        self.resized_since_last_board_draw = True

    def draw_board(self):
        """Draw the Sudoku board on the screen."""

        may_require_square_redraw = self.resized_since_last_board_draw or not self.solved
        if may_require_square_redraw:
            for row_indx in range(9):
                for col_indx in range(9):
                    is_user_input = self.initial_board[row_indx][col_indx] == 0

                    coords = (row_indx, col_indx)
                    colour = (
                        "black"
                        if not is_user_input
                        else HINT_COLOUR
                        if coords in self.hinted_squares_coords
                        else SOLVED_COLOUR
                        if coords in self.solved_squares_coords
                        else CORRECT_COLOUR
                        if coords in self.correct_squares_coords
                        else WRONG_COLOUR
                        if coords in self.incorrect_squares_coords
                        else INPUT_COLOUR
                    )

                    if (
                        len(self.squares) > (square_indx := row_indx * 9 + col_indx)
                        and not self.resized_since_last_board_draw
                    ):
                        # This square has been drawn before
                        square_rect, square_number = self.squares[square_indx]

                        if (new_number := self.board[row_indx][col_indx]) != square_number:
                            # The number in the square has changed
                            x = square_rect.x
                            y = square_rect.y

                            # Draw the number
                            self.squares[square_indx] = (square_rect, new_number)
                            pygame.draw.rect(self.screen, "white", square_rect)
                            self.draw_number(
                                new_number,
                                x,
                                y,
                                colour=colour,
                            )

                    else:
                        # First time drawing this square

                        x = self.get_x_of_square(col_indx)
                        y = self.get_y_of_square(row_indx)

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
                            colour=colour,
                        )

            if self.prev_selected != self.selected:
                if self.prev_selected in self.correct_squares_coords:
                    # The previously selected square is now known to be correct
                    # and has therefore already been redrawn, so don't draw it again
                    self.prev_selected = None
                    return

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
                        # NB: It's not possible to select a correct/hinted/solved square, so we don't have to handle those cases here
                        colour=WRONG_COLOUR if self.prev_selected in self.incorrect_squares_coords else INPUT_COLOUR,
                    )

                currently_selected_square = (
                    self.squares[self.selected[0] * 9 + self.selected[1]] if self.selected else None
                )
                if currently_selected_square:
                    pygame.draw.rect(self.screen, "yellow", currently_selected_square[0])
                    self.draw_number(
                        currently_selected_square[1],
                        currently_selected_square[0].x,
                        currently_selected_square[0].y,
                        # NB: It's not possible to select a correct/hinted/solved square, so we don't have to handle those cases here
                        colour=WRONG_COLOUR if self.selected in self.incorrect_squares_coords else INPUT_COLOUR,
                    )

                self.prev_selected = self.selected

            if self.resized_since_last_board_draw:
                self.draw_buttons()
                self.resized_since_last_board_draw = False

        if self.solved:
            font = pygame.font.Font(None, 90)  # TODO: Figure out dynamic font size based on square size
            text = font.render("           Congrats!\nYou solved the Sudoku!", True, CORRECT_COLOUR)
            text_rect = text.get_rect(center=(self.actual_screen_width // 2, self.actual_screen_height // 2))
            self.screen.blit(text, text_rect)

    def draw_buttons(self):
        """Draw the buttons on the screen."""

        for btn_indx, button in enumerate(self.buttons):
            button_x = self.bold_border_width + (btn_indx * (self.btn_width + self.bold_border_width))
            button_y = self.get_y_of_square(9)

            button["rect"] = pygame.Rect(
                button_x,
                button_y,
                self.btn_width,
                self.btn_height,
            )

            pygame.draw.rect(
                self.screen,
                button["colour"],
                button["rect"],
            )
            font = pygame.font.Font(None, 36)  # TODO: Figure out dynamic font size based on square size
            text = font.render(button["name"], True, "black")
            text_rect = text.get_rect(center=(button_x + self.btn_width // 2, button_y + self.btn_height // 2))
            self.screen.blit(text, text_rect)

    def draw_number(self, number, x, y, colour="black"):
        text = str(number) if number else " "

        font = pygame.font.Font(None, 36)  # TODO: Figure out dynamic font size based on square size
        font.set_italic(colour == INPUT_COLOUR)
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

    def handle_verify_button_clicked(self):
        if self.solved:
            return

        print("DEBUG: Verify button clicked")

        incorrect_square_indexes = SudokuValidator.get_incorrect_squares(self.solved_board, self.board)
        for unsure_square_indx in self.unsure_squares_coords.copy():
            row_indx, col_indx = unsure_square_indx

            square_indx = row_indx * 9 + col_indx
            square_rect, square_number = self.squares[square_indx]

            if unsure_square_indx in incorrect_square_indexes:
                colour = WRONG_COLOUR
                self.incorrect_squares_coords.add(unsure_square_indx)
            else:
                colour = CORRECT_COLOUR
                self.correct_squares_coords.add(unsure_square_indx)

            self.unsure_squares_coords.discard(unsure_square_indx)

            pygame.draw.rect(self.screen, "white", square_rect)
            self.draw_number(
                square_number,
                square_rect.x,
                square_rect.y,
                colour=colour,
            )

    def handle_solve_button_clicked(self):
        if self.solved:
            return

        print("DEBUG: Solve button clicked")

        for row_indx, row in enumerate(self.solved_board):
            for col_indx, correct_number in enumerate(row):
                coords = (row_indx, col_indx)
                square_indx = row_indx * 9 + col_indx
                square_rect, number_in_square = self.squares[square_indx]

                if number_in_square == correct_number:
                    # NB: Don't have to include solved squares, since it's impossible to have solved squares in an unsolved game
                    known_correct_squares = self.correct_squares_coords.union(self.hinted_squares_coords)

                    if self.initial_board[row_indx][col_indx] == 0 and coords not in known_correct_squares:
                        pygame.draw.rect(self.screen, "white", square_rect)
                        self.draw_number(correct_number, square_rect.x, square_rect.y, colour=CORRECT_COLOUR)
                        self.unsure_squares_coords.discard(coords)
                        self.correct_squares_coords.add(coords)
                    continue

                self.board[row_indx][col_indx] = correct_number
                self.squares[square_indx] = (square_rect, correct_number)

                if number_in_square == 0:
                    # hasn't entered a number yet
                    colour = SOLVED_COLOUR
                    self.solved_squares_coords.add(coords)
                else:
                    # has entered a number, but is was wrong
                    colour = WRONG_COLOUR
                    self.incorrect_squares_coords.add(coords)

                self.unsure_squares_coords.discard(coords)

                pygame.draw.rect(self.screen, "white", square_rect)
                self.draw_number(
                    correct_number,
                    square_rect.x,
                    square_rect.y,
                    colour=colour,
                )

                self.solved = True

    def handle_hint_button_clicked(self):
        if self.solved:
            return

        print("DEBUG: Hint button clicked")

        for row_indx, row in enumerate(self.board):
            for col_indx, current_number in enumerate(row):
                if current_number != 0:
                    continue

                coords = (row_indx, col_indx)
                square_indx = row_indx * 9 + col_indx
                square_rect = self.squares[square_indx][0]

                correct_number = self.solved_board[row_indx][col_indx]

                pygame.draw.rect(self.screen, "white", square_rect)
                self.draw_number(
                    correct_number,
                    square_rect.x,
                    square_rect.y,
                    colour=HINT_COLOUR,
                )
                self.board[row_indx][col_indx] = correct_number
                self.squares[square_indx] = (square_rect, correct_number)
                self.hinted_squares_coords.add(coords)

                if SudokuValidator.is_valid_sudoku(self.board, allow_empty=False):
                    self.solved = True

                return  # Only show one hint at a time

    def handle_mouse_click(self, pos: tuple[int, int]):
        """Handle mouse click events to select a square."""

        x, y = pos

        # TODO: Possibly refactor to utilise `self.squares` instead of this for loop? Maybe refactor into get_cell_indexes_at_pos()?
        for row_indx in range(10):  # NB: 9 rows for squares + 1 row for buttons
            if row_indx == 9:
                # Clicked on a button
                for button in self.buttons:
                    if button["rect"] and button["rect"].collidepoint(x, y):
                        # Button clicked
                        button["on_click"]()
                        return
                continue

            for col_indx in range(9):
                rect = pygame.Rect(
                    self.get_x_of_square(col_indx),
                    self.get_y_of_square(row_indx),
                    self.square_width,
                    self.square_height,
                )
                if rect.collidepoint(x, y):
                    # Clicked on a square

                    # NB: Don't have to include solved squares, since it's
                    # impossible to have solved squares in an unsolved game
                    known_correct_squares = self.correct_squares_coords.union(self.hinted_squares_coords)

                    if (
                        not self.solved  # game is still unsolved
                        and self.initial_board[row_indx][col_indx] == 0  # square is one that requires user input
                        and (coords := (row_indx, col_indx))
                        not in known_correct_squares  # square is not already solved
                    ):
                        if self.selected == coords:
                            self.selected = None
                        else:
                            self.selected = coords
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

            self.unsure_squares_coords.add(self.selected)
            self.incorrect_squares_coords.discard(self.selected)
            self.selected = None

            print(f"DEBUG: {self.board = }")
            if SudokuValidator.is_valid_sudoku(self.board, allow_empty=False):
                print("DEBUG: Sudoku solved!")
                self.solved = True

    def update_screen_size(self, new_width, new_height):
        """Handle screen resizing events."""
        if new_width < MIN_WIDTH:
            self.screen = pygame.display.set_mode(self.prev_size, pygame.RESIZABLE)
            self.resized_since_last_board_draw = True
            print(f"DEBUG: Resize event ignored (width too small). {new_width = } {new_height = }")
            return

        if new_height < MIN_HEIGHT:
            self.screen = pygame.display.set_mode(self.prev_size, pygame.RESIZABLE)
            self.resized_since_last_board_draw = True
            print(f"DEBUG: Resize event ignored (height too small). {new_width = } {new_height = }")
            return

        if new_width > pygame.display.Info().current_w or new_height > pygame.display.Info().current_h:
            self.screen = pygame.display.set_mode(self.prev_size, pygame.RESIZABLE)
            self.resized_since_last_board_draw = True
            print(f"DEBUG: Resize event ignored (too big). {new_width = } {new_height = }")
            return

        self.squares: list[tuple[pygame.Rect, int]] = []

        self.actual_screen_width = new_width
        self.actual_screen_height = new_height
        self.calculate_dimensions()

    def game_loop(self):
        """Main game loop."""
        self.draw_buttons()  # NB: We only need to draw the buttons once, since they don't change

        running = True
        prev_solved = self.solved
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

            if self.solved == prev_solved:
                if not self.solved or self.resized_since_last_board_draw:
                    self.draw_board()
            else:
                # Solved state was toggled
                if self.solved:
                    prev_solved = True
                    self.draw_board()

            pygame.display.flip()
            self.clock.tick(FPS)

    def play(self):
        """Start the game."""
        self.generator = SudokuGenerator(self.difficulty)
        self.solved_board, self.initial_board = self.generator.generate_random_sudoku()

        SudokuRenderer.draw_sudoku_to_terminal(self.solved_board)
        SudokuRenderer.draw_sudoku_to_terminal(self.initial_board)

        self.board = [row.copy() for row in self.initial_board]
        self.prev_selected: tuple[int, int] | None = None
        self.selected: tuple[int, int] | None = None
        self.solved = False
        self.squares = []

        self.buttons: list[Button] = [
            {"name": "Hint", "colour": HINT_COLOUR, "on_click": self.handle_hint_button_clicked, "rect": None},
            {"name": "Verify", "colour": "bisque", "on_click": self.handle_verify_button_clicked, "rect": None},
            {"name": "Solve", "colour": CORRECT_COLOUR, "on_click": self.handle_solve_button_clicked, "rect": None},
            {"name": "New Game", "colour": "red", "on_click": self.play, "rect": None},
        ]

        self.hinted_squares_coords: set[tuple[int, int]] = set()
        self.solved_squares_coords: set[tuple[int, int]] = set()
        self.incorrect_squares_coords: set[tuple[int, int]] = set()
        self.correct_squares_coords: set[tuple[int, int]] = set()
        self.unsure_squares_coords: set[tuple[int, int]] = set()

        self.actual_screen_width = self.target_screen_width
        self.actual_screen_height = self.target_screen_height

        self.calculate_dimensions()
        self.clock = pygame.time.Clock()

        self.game_loop()
        pygame.quit()
