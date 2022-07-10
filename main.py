import copy
import sys
import pygame
import Button
import random

FPS = 60

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (150, 0, 0)
DARKEST_RED = (100, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
GREY = (196, 196, 196)
PURPLE = (155, 0, 255)
TEAL = (0, 170, 255)
YELLOW = (245, 255, 10)
LIGHT_BLUE = (130, 190, 240)
LIGHT_GREY = (215, 215, 215)
DARK_GREY = (96, 96, 96)
DARK_ORANGE = (205, 100, 0)
BUTTON_BLUE = (25, 120, 255)


# GUI parameters
SQUARE_SIDE_LENGTH = 50
LINE_THICKNESS = 2
DIVIDER_THICKNESS = 8
GUI_HEIGHT = 250
ROWS = 9
COLUMNS = 9
SCREEN_BORDER = 20


SCREEN_HEIGHT = GUI_HEIGHT + ((SQUARE_SIDE_LENGTH + LINE_THICKNESS) * ROWS) - (LINE_THICKNESS * 2) + (
        DIVIDER_THICKNESS * 4) + (SCREEN_BORDER * 2)
SCREEN_WIDTH = ((SQUARE_SIDE_LENGTH + LINE_THICKNESS) * COLUMNS) + LINE_THICKNESS - (LINE_THICKNESS * 2) + (
        DIVIDER_THICKNESS * 4) + (SCREEN_BORDER * 2)

pygame.init()
clock = pygame.time.Clock()
screen_display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Sudoku Solver")

screen_border_rect = pygame.Rect([0, 0, SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.draw.rect(screen_display, DARK_GREY, screen_border_rect)

screen_rect = pygame.Rect([SCREEN_BORDER, SCREEN_BORDER, SCREEN_WIDTH - (SCREEN_BORDER*2), SCREEN_HEIGHT - (SCREEN_BORDER*2)])
pygame.draw.rect(screen_display, BLACK, screen_rect)

font = pygame.font.SysFont('Sans', 18, True, False)  # Font name, size, bold, italics
numbers_font = pygame.font.SysFont('Sans', 20, True, False)

class Cell:
    def __init__(self, x, y, row, column, color, number=0, original=False):
        self.original = original
        self.color = color
        self.number = number
        self.x = x
        self.y = y
        self.row = row
        self.column = column
        self.rect = pygame.Rect(self.x, self.y, SQUARE_SIDE_LENGTH, SQUARE_SIDE_LENGTH)
        self.valid_row = True
        self.valid_column = True
        self.valid_square = True
        self.original_color = color
        self.number_color = None

    def change_valid_row(self, v):
        self.valid_row = v

    def change_valid_column(self, v):
        self.valid_column = v

    def change_valid_square(self, v):
        self.valid_square = v

    def __eq__(self, other):
        return self.number == other.number

    def __hash__(self):  # for use in sets
        return hash(self.number)

    def get_position(self):
        return self.x, self.y

    def draw_cell_numbers(self):
        if not self.number_color:
            if self.original:
                number_color = BLACK
            else:
                number_color = TEAL
        else:
            number_color = self.number_color

        if self.number != 0:
            number_image = numbers_font.render(str(self.number), True, number_color, self.color)
            center_x = (SQUARE_SIDE_LENGTH - number_image.get_width()) // 2
            center_y = (SQUARE_SIDE_LENGTH - number_image.get_height()) // 2
            screen_display.blit(number_image, (self.x + center_x, self.y + center_y))

    def is_hovered(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            return True

        else:
            return False

    def color_hover(self):
        self.color = YELLOW

    def reset_color(self):
        self.color = self.original_color

    def change_number_color(self, color):
        self.number_color = color

    def change_cell_color(self, color):
        self.color = color
        self.original_color = color

    def increment_cell(self):
        if not self.original:
            self.number += 1
            if self.number > 9:
                self.number = 0

    def decrement_cell(self):
        if not self.original:
            self.number -= 1
            if self.number < 0:
                self.number = 9

    def change_cell_number(self, number):
        self.number = number

    def get_invalid_count(self):
        c = 0
        if not self.valid_row:
            c += 1
        if not self.valid_column:
            c += 1
        if not self.valid_square:
            c += 1
        return c

    def print_cell_validity(self):
        print("row: " + str(self.valid_row),
              "column: " + str(self.valid_column),
              "square: " + str(self.valid_square))


def check_if_buttons_hovered(buttons_list):
    for button in buttons_list:
        if button.is_hovered():
            button.change_button_color(LIGHT_BLUE)
        else:
            button.change_button_color(button.original_color)


def create_buttons():
    buttons_list = []

    x1 = 70
    y1 = SCREEN_HEIGHT - GUI_HEIGHT

    reset_button = Button.Button("reset_button", x1, y1, "   Reset   ", WHITE, BUTTON_BLUE, font)
    buttons_list.append(reset_button)

    x2 = x1 + 100
    done_button = Button.Button("done_button", x2, y1, "   Done   ", WHITE, BUTTON_BLUE, font)
    buttons_list.append(done_button)

    x3 = x2 + 100

    check_button = Button.Button("check_button", x3, y1, "   Check   ", WHITE, BUTTON_BLUE, font)
    buttons_list.append(check_button)

    x4 = x3 + 100
    x5 = 200
    y2 = y1 + 50
    new_grid_button = Button.Button("new_grid_button", x4, y1, "   New Grid   ", WHITE, BUTTON_BLUE, font)

    buttons_list.append(new_grid_button)
    solve_button = Button.Button("solve_button", x5, y2, "   Get Solution   ", WHITE, BUTTON_BLUE, font)
    buttons_list.append(solve_button)

    return buttons_list


def draw_GUI(buttons_list):
    for button in buttons_list:
        border_rect = pygame.Rect([button.x -2, button.y -2, button.rect.w + 4, button.rect.h + 4])
        pygame.draw.rect(screen_display, DARK_ORANGE, border_rect)
        pygame.draw.rect(screen_display, button.button_color, button.rect)
        screen_display.blit(button.text, button.text_rect)


def draw_console(console_message):
    pos_x = 25
    pos_y = SCREEN_HEIGHT - GUI_HEIGHT + 90
    console_rect = pygame.Rect([pos_x, pos_y, SCREEN_WIDTH - 50, 140])
    border_width = 5
    console_border_rect = pygame.Rect([pos_x - border_width, pos_y - border_width, SCREEN_WIDTH - 50 + (border_width * 2),
                                       140 + (border_width * 2)])
    pygame.draw.rect(screen_display, GREY, console_border_rect)
    pygame.draw.rect(screen_display, BLACK, console_rect)
    buffer = 5
    x, y = pos_x + buffer, pos_y + buffer
    space_x_size = font.size(" ")[0]  # x value, width of each space
    words = console_message.split(" ")

    for word in words:
        if word.lower() == "red.":
            word_surface = font.render(word, True, RED)
        else:
            word_surface = font.render(word, True, WHITE)
        word_width, word_height = word_surface.get_size()

        if x + word_width > console_rect.w - (buffer * 2):
            x = pos_x + buffer
            y += word_height + buffer
        screen_display.blit(word_surface, (x, y))
        x += word_width + space_x_size


def create_sudoku_grid(sample):
    grid = [[] for _ in range(ROWS)]
    y = DIVIDER_THICKNESS + SCREEN_BORDER

    for row in range(ROWS):
        x = DIVIDER_THICKNESS + SCREEN_BORDER
        for column in range(COLUMNS):
            x_coord = x + LINE_THICKNESS
            y_coord = y + LINE_THICKNESS

            if sample[row][column] == 0:
                original = False
            else:
                original = True

            cell = Cell(x_coord, y_coord, row, column, WHITE, sample[row][column], original)
            grid[row].append(cell)

            x += LINE_THICKNESS + SQUARE_SIDE_LENGTH

            if (column + 1) % 3 == 0:
                x += DIVIDER_THICKNESS - LINE_THICKNESS
        y += LINE_THICKNESS + SQUARE_SIDE_LENGTH
        if (row + 1) % 3 == 0:
            y += DIVIDER_THICKNESS - LINE_THICKNESS
    return grid


def create_solved_grid(solved_grid, original_grid):
    grid = [[] for _ in range(ROWS)]
    y = DIVIDER_THICKNESS + SCREEN_BORDER

    for row in range(ROWS):
        x = DIVIDER_THICKNESS + SCREEN_BORDER
        for column in range(COLUMNS):
            x_coord = x + LINE_THICKNESS
            y_coord = y + LINE_THICKNESS

            if original_grid[row][column] == 0:
                change_number_color = True

            else:
                change_number_color = False

            cell = Cell(x_coord, y_coord, row, column, WHITE, solved_grid[row][column], True)

            if change_number_color:
                cell.change_number_color(PURPLE)
            grid[row].append(cell)

            x += LINE_THICKNESS + SQUARE_SIDE_LENGTH

            if (column + 1) % 3 == 0:
                x += DIVIDER_THICKNESS - LINE_THICKNESS

        y += LINE_THICKNESS + SQUARE_SIDE_LENGTH

        if (row + 1) % 3 == 0:
            y += DIVIDER_THICKNESS - LINE_THICKNESS

    return grid


def reset_grid(original_grid):
    original = create_sudoku_grid(original_grid)
    return original

def draw_grid(sudoku_grid):
    for row in range(ROWS):
        for column in range(COLUMNS):
            pygame.draw.rect(screen_display, sudoku_grid[row][column].color,
                             sudoku_grid[row][column].rect
                             )
            sudoku_grid[row][column].draw_cell_numbers()


def click_on_cell(sudoku_grid, inc):
    for row in sudoku_grid:
        for cell in row:
            if cell.is_hovered() and not cell.original:
                if inc:
                    cell.increment_cell()
                else:
                    cell.decrement_cell()
                # print(cell.row, cell.column)
                check_for_errors(cell, sudoku_grid)


def check_for_errors(cell, sudoku_grid):
    check_row(sudoku_grid, cell)
    check_column(sudoku_grid, cell)
    check_square(sudoku_grid, cell)

    for row in sudoku_grid:
        for cell in row:
            c = cell.get_invalid_count()
            if c == 0:
                cell.change_cell_color(WHITE)
            elif c == 1:
                cell.change_cell_color(RED)
            elif c == 2:
                cell.change_cell_color(DARK_RED)
            else:
                cell.change_cell_color(DARKEST_RED)


def check_row(sudoku_grid, cell):
    row = sudoku_grid[cell.row]
    l = []
    for c in row:
        if c.number:
            l.append(c)

    if len(set(l)) < len(l):
        for c in row:
            c.change_valid_row(False)

    else:
        for c in row:
            c.change_valid_row(True)


def check_column(sudoku_grid, cell):
    column_index = cell.column
    o = []
    l = []
    for row in sudoku_grid:
        c = row[column_index]
        if c.number:
            l.append(c)
        o.append(c)
    if len(set(l)) < len(l):
        for e in o:
            e.change_valid_column(False)
    else:
        for e in o:
            e.change_valid_column(True)


def check_square(sudoku_grid, cell):
    x = (cell.column // 3) * 3
    y = (cell.row // 3) * 3
    valid = True
    o = []
    l = []
    for i in range(3):
        for j in range(3):
            if sudoku_grid[y + i][x + j].number:
                l.append(sudoku_grid[y + i][x + j].number)
            o.append(sudoku_grid[y + i][x + j].number)

    if len(set(l)) < len(l):
        valid = False

    if not valid:
        for i in range(3):
            for j in range(3):
                e = sudoku_grid[y + i][x + j]

                e.change_valid_square(False)

    else:
        for i in range(3):
            for j in range(3):
                e = sudoku_grid[y + i][x + j]
                e.change_valid_square(True)


def clicked_in_GUI():
    mouse_position = pygame.mouse.get_pos()

    if 0 <= mouse_position[0] <= SCREEN_WIDTH:
        if SCREEN_HEIGHT - GUI_HEIGHT <= mouse_position[1] <= SCREEN_HEIGHT:
            return True
    return False

# not used as now only using grids with one solution
def on_click_solve(solved_grids, original_grid, button):  # randomly generated will only have one solution anyway
    button.counter += 1

    if button.counter >= len(solved_grids):
        button.counter = 0

    solved_grid = solved_grids[button.counter]
    return create_solved_grid(solved_grid, original_grid)


def check_grid(sudoku_grid):
    no_mistakes = True
    empty_cell = False
    for row in range(9):
        for column in range(9):
            color = sudoku_grid[row][column].color
            if color == RED or color == DARK_RED or color == DARKEST_RED:
                no_mistakes = False
            if sudoku_grid[row][column].number == 0:
                empty_cell = True

    if no_mistakes and not empty_cell:
        for row in range(9):
            for column in range(9):
                sudoku_grid[row][column].change_cell_color(GREEN)

    return no_mistakes, empty_cell


def check_if_cells_hovered(sudoku_grid):
    cell_hovered = None
    for row in sudoku_grid:
        for cell in row:
            if cell.is_hovered() and not cell.original:
                cell.color_hover()
                cell_hovered = cell
                # cell.print_cell_validity()
                # return statement here will not work - will make it slower and can cause cells to stay hovered when
                # the mouse is no longer on them.
            else:
                cell.reset_color()
    return cell_hovered

def count_empty_cells(grid):
    count = 0
    for y in range(9):
        for x in range(9):
            if not type(grid[y][x]) == Cell:
                if grid[y][x] == 0:
                    count += 1
            else:
                if grid[y][x].number == 0:
                    count += 1
    return count


def type_to_cell(cell, sudoku_grid, num):
    cell.number = num
    cell.valid_column = True
    cell.valid_row = True
    cell.valid_square = True
    check_row(sudoku_grid, cell)
    check_column(sudoku_grid, cell)
    check_square(sudoku_grid, cell)


def display_invalid_grid(sudoku_grid):
    message = "There are still mistakes on the board! They are shown in red."
    timer = 60
    flash_red = False

    F = 10
    stay_red_time = F
    while timer > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if flash_red:
            for row in range(9):
                for column in range(9):
                    if sudoku_grid[row][column].color == WHITE:
                        sudoku_grid[row][column].color = sudoku_grid[row][column].original_color

            stay_red_time -= 1
            if stay_red_time == 0:
                flash_red = False
                stay_red_time = F

        elif timer > 0:
            for row in range(9):
                for column in range(9):
                    color = sudoku_grid[row][column].color
                    if color == RED or color == DARK_RED or color == DARKEST_RED:
                        sudoku_grid[row][column].color = WHITE

            stay_red_time -= 1
            if stay_red_time == 0:
                flash_red = True
                stay_red_time = F

        timer -= 1
        draw_grid(sudoku_grid)
        draw_console(message)
        pygame.display.update()
        clock.tick(FPS)


def number_cells_removed(cell_difference):
    if cell_difference == 0:
        return " 0 Cells cleared."
    elif cell_difference == 1:
        return " 1 Cell cleared."
    else:
        return f"{cell_difference} Cells cleared."

def find_non_colored_mistakes(sudoku_grid, solved_grid):
    non_colored_mistake = False
    for row in range(9):
        for column in range(9):
            color = sudoku_grid[row][column].color
            if sudoku_grid[row][column].number != 0:
                if not (color == RED or color == DARK_RED or color == DARKEST_RED):
                    if solved_grid[row][column] != sudoku_grid[row][column].number:
                        sudoku_grid[row][column].change_cell_color(PURPLE)
                        non_colored_mistake = True

    return non_colored_mistake


def main():
    sample_grid2 = [[7, 0, 0, 0, 0, 0, 0, 2, 0],
                    [0, 0, 0, 1, 7, 9, 6, 4, 3],
                    [0, 0, 0, 0, 2, 5, 0, 0, 0],
                    [4, 0, 5, 0, 6, 0, 3, 8, 0],
                    [8, 0, 0, 0, 0, 0, 0, 0, 9],
                    [0, 1, 9, 0, 4, 0, 2, 0, 6],
                    [0, 0, 0, 3, 5, 0, 0, 0, 0],
                    [9, 7, 6, 4, 8, 1, 0, 0, 0],
                    [0, 4, 0, 0, 0, 0, 0, 0, 8]]

    original_grid = sample_grid2.copy()
    sudoku_grid = create_sudoku_grid(sample_grid2)

    buttons_list = create_buttons()
    list_solved_grids = get_solved_grids(original_grid, [])
    solved_grid = list_solved_grids[0]
    # print(len(list_solved_grids))
    # print(list_solved_grids)

    default_message = "Mouse over cell and type a number to fill that cell in. 0 clears a cell. " \
                      "Alternatively, click on cells to increment or decrement their numbers with  left click " \
                      "and right click respectively. " \
                      "Mistakes will have a row's, column's and/or square's tiles colored in RED."

    reset_message = "The board has been reset to its original state. "
    solved = False
    message = default_message
    while True:

        selected_cell = check_if_cells_hovered(sudoku_grid)
        check_if_buttons_hovered(buttons_list)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                #message = default_message
                mouse_button = event.button
                if mouse_button == 1 and not clicked_in_GUI() and not solved:
                    click_on_cell(sudoku_grid, True)

                elif mouse_button == 3 and not clicked_in_GUI() and not solved:
                    click_on_cell(sudoku_grid, False)

                elif mouse_button == 1 and clicked_in_GUI():
                    for button in buttons_list:
                        #if button.is_clicked(event):
                        if button.is_hovered():
                            if button.button_name == "reset_button":

                                cell_difference = abs(count_empty_cells(sudoku_grid) - count_empty_cells(original_grid))
                                sudoku_grid = reset_grid(original_grid)

                                message = reset_message + number_cells_removed(cell_difference)

                            elif button.button_name == "done_button":

                                no_mistakes, empty_cell = check_grid(sudoku_grid)
                                solved = no_mistakes and not empty_cell
                                if solved:
                                    message = "This puzzle has been solved! Click on generate new grid to start " \
                                              "a new puzzle."

                                else:
                                    if not no_mistakes:
                                        display_invalid_grid(sudoku_grid)
                                        message = "There are still mistakes on the board! They are shown in red."
                                    else:
                                        message = "The board still has empty cells!"

                            elif button.button_name == "solve_button":
                                sudoku_grid = create_solved_grid(solved_grid, original_grid)
                                # on_click_solve(list_solved_grids, original_grid, button)
                                message = "This sudoku grid has been solved by the program."
                            elif button.button_name == "new_grid_button":

                                sudoku_grid, original_grid = generate_sudoku()
                                list_solved_grids = get_solved_grids(original_grid, [])
                                solved_grid = list_solved_grids[0]
                                solved = False
                                message = "A new randomized sudoku grid has been generated."
                                # print()
                                # print("number of possible solved grids for this grid: ")
                                # print(len(list_solved_grids))

                            elif button.button_name == "check_button":

                                no_mistakes, empty_cell = check_grid(sudoku_grid)
                                non_colored_mistake = find_non_colored_mistakes(sudoku_grid, solved_grid)
                                solved = no_mistakes and not empty_cell
                                if solved:
                                    message = "This puzzle has been solved! Click on generate new grid to start " \
                                              "a new puzzle."
                                else:
                                    if not no_mistakes:
                                        display_invalid_grid(sudoku_grid)
                                        message = "There are still mistakes on the board! They are shown in red."

                                    elif non_colored_mistake:
                                        message = "There is at least one mistake made, highlighted in purple."
                                    else:
                                        message = "No mistakes so far."

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    cell_difference = abs(count_empty_cells(sudoku_grid) - count_empty_cells(original_grid))
                    sudoku_grid = reset_grid(original_grid)
                    message = reset_message + number_cells_removed(cell_difference)
                elif selected_cell:
                    message = default_message
                    if event.key == pygame.K_0:
                        num = 0
                    elif event.key == pygame.K_1:
                        num = 1
                    elif event.key == pygame.K_2:
                        num = 2
                    elif event.key == pygame.K_3:
                        num = 3
                    elif event.key == pygame.K_4:
                        num = 4
                    elif event.key == pygame.K_5:
                        num = 5
                    elif event.key == pygame.K_6:
                        num = 6
                    elif event.key == pygame.K_7:
                        num = 7
                    elif event.key == pygame.K_8:
                        num = 8
                    elif event.key == pygame.K_9:
                        num = 9
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE or event.key == pygame.K_c:
                        num = 0

                    else:
                        num = None

                    if num:
                        selected_cell.change_cell_number(num)
                        check_for_errors(selected_cell, sudoku_grid)
                        num = None

        draw_GUI(buttons_list)
        draw_console(message)
        draw_grid(sudoku_grid)

        pygame.display.update()
        clock.tick(FPS)


def get_solved_grids(original_grid, solved_grids_list):
    for y in range(9):
        for x in range(9):
            if original_grid[y][x] == 0:
                for n in range(1, 10):
                    if check_if_num_valid(x, y, n, original_grid):
                        original_grid[y][x] = n
                        get_solved_grids(original_grid, solved_grids_list)
                        original_grid[y][x] = 0 # reset cell to empty if above doesn't work
                return solved_grids_list

    solved_grids_list.append(copy.deepcopy(original_grid))


def check_if_num_valid(x, y, n, grid):

    # check the square
    top_left_x = (x // 3) * 3
    top_left_y = (y // 3) * 3
    for i in range(3):
        for j in range(3):
            if grid[top_left_y + i][top_left_x + j] == n:
                return False


    # check row
    for i in range(9):
        if grid[y][i] == n:
            return False

    # check column
    for i in range(9):
        if grid[i][x] == n:
            return False
    return True



def check_if_grid_full(grid):
    for y in range(9):
        for x in range(9):
            if grid[y][x] == 0:
                return False
    return True


def generate_sudoku():
    base_grid = [[0] * 9 for _ in range(9)]

    generate_random_sudoku(base_grid)  # creates a fully filled in random sudoku by modifying base_grid
    grid = base_grid
    # iterate over every number in the grid and check if the number can be removed while keeping only 1 solution.
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            random_row, random_column = random.randint(0, 8), random.randint(0, 8)

            number = grid[random_row][random_column]
            grid[random_row][random_column] = 0

            if len(get_solved_grids(grid, [])) != 1:
                grid[random_row][random_column] = number

    random_num = random.randint(0, 3)
    for i in range(random_num):
        rotate_by_90(grid)

    random_flip = random.randint(0, 3)

    if random_flip == 0:
        flip_horizontal(grid)
    elif random_flip == 1:
        flip_vertical(grid)
    else:

        if random_flip == 2:
            flip_horizontal(grid)
            flip_vertical(grid)
        else:
            flip_vertical(grid)
            flip_horizontal(grid)
    original = copy.deepcopy(grid)
    # print_grid_numbers(grid)
    return create_sudoku_grid(grid), original

def generate_random_sudoku(grid):
    values = [i for i in range(1, 10)]
    row, column = None, None
    for y in range(9):
        for x in range(9):
            row = y
            column = x
            if grid[y][x] == 0:
                random.shuffle(values)
                for value in values:
                    if check_if_num_valid(x, y, value, grid):
                        grid[y][x] = value

                        if check_if_grid_full(grid):
                            return True
                        else:

                            if generate_random_sudoku(grid):
                                return True
                break # didn't return True
        else:  # is only executed when inner loop finishes without breaking
            continue
        break

    grid[row][column] = 0
    return False


def rotate_by_90(grid):
    n = len(grid)
    r = len(grid[0])
    for i in range(n):
        for j in range(i, r):
            grid[i][j], grid[j][i] = grid[j][i], grid[i][j]
    for row in grid:
        row.reverse()


def flip_horizontal(grid):
    for row in grid:
        row.reverse()


def flip_vertical(grid):
    c = len(grid)
    n = c // 2

    for i in range(n):
        for j in range(len(grid[n])):
            grid[i][j], grid[c - 1 - i][j] = grid[c - 1 - i][j], grid[i][j]


def print_grid_numbers(grid):
    for y in range(9):
        for x in range(9):
            if grid[y][x] == 0:
                print(" ", end="")
            else:
                print(grid[y][x], end="")
    print()


if __name__ == "__main__":
    main()
