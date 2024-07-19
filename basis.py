import pygame
from constants import *


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.half_size = (self.half_width, self.half_height)

    def put_in_center(self, target_spr):
        self.rect.center = target_spr.half_size

    def draw_in_center(self, target_spr):
        self.put_in_center(target_spr)
        target_spr.image.blit(self.image, self.rect)

    def draw_border(self, border):
        border_width = border[0]
        border_color = border[1]
        pygame.draw.rect(self.image, border_color, (0, 0, self.width, border_width))
        pygame.draw.rect(self.image, border_color,
                         (0, self.height - border_width, self.width, border_width))
        pygame.draw.rect(self.image, border_color, (0, 0, border_width, self.height))
        pygame.draw.rect(self.image, border_color,
                         (self.width - border_width, 0, border_width, self.height))



class Font(pygame.font.Font):

    pixelated = 'assets/pixelated.ttf'

    def __init__(self, font, size):
        super().__init__(font, size)
        self.size = size

    def center_write(self, msg, color, target_spr, pos):
        image = self.render(msg, True, color)
        rect = image.get_rect()
        rect.center = pos
        target_spr.image.blit(image, rect)

    def topleft_write(self, msg, color, target_spr, pos):
        image = self.render(msg, True, color)
        rect = image.get_rect()
        rect.topleft = pos
        target_spr.image.blit(image, rect)



class Screen:

    width = 1000
    height = 650
    size = (width, height)
    window = pygame.display.set_mode(size)
    half_size = tuple(x / 2 for x in size)

    @classmethod
    def draw_return_msg(cls):
        font = Font(Font.pixelated, 20)
        subrect = pygame.Rect(10, 10, 200, 200)
        spr = Sprite(Screen.window.subsurface(subrect))
        font.topleft_write('ESC para voltar', WHITE, spr, (0, 0))



class Tile(Sprite):

    unrevealed_color = CYAN
    revealed_color = BLACK

    def __init__(self, correct, size, color = None):
        self.size = size
        super().__init__(pygame.Surface((self.size,) * 2))

        self.correct = correct
        self.color = color if self.correct else None
        self.revealed = False
        self.marked_wrong = False
        self.matrix_pos = (0, 0)

    def reveal(self):
        if not self.revealed:
            self.revealed = True
            self.image.fill(Tile.revealed_color)

    def mark_wrong(self, left_click = False):
        if self.marked_wrong and not left_click:
            pygame.draw.line(self.image, Tile.unrevealed_color, (0, 0), (self.rect.width, self.rect.height))
            pygame.draw.line(self.image, Tile.unrevealed_color, (self.rect.width, 0), (0, self.rect.height))
            self.draw_border((3, BLACK))
            self.marked_wrong = False
        else:
            pygame.draw.line(self.image, BLACK, (0, 0), (self.rect.width, self.rect.height))
            pygame.draw.line(self.image, BLACK, (self.rect.width, 0), (0, self.rect.height))
            self.marked_wrong = True




class Level(Sprite):

    levels = []
    border = (6, BLACK)

    def __init__(self, tile_size, matrix):
        Level.levels.append(self)

        self.number = len(Level.levels)
        self.tile_size = tile_size

        self.matrix = self.translate_matrix(matrix)

        self.rows_amount = len(self.matrix)
        self.cols_amount = len(self.matrix[0])
        self.rows_numbers = self.get_rows_numbers()
        self.cols_numbers = self.get_cols_numbers()

        self.tiles = self.get_tiles()

        w = self.cols_amount * self.tile_size
        h = self.rows_amount * self.tile_size
        super().__init__(pygame.Surface((w, h)))

    def translate_matrix(self, matrix):
        for i, row in enumerate(matrix):
            for j, color in enumerate(row):

                if color != 0:
                    matrix[i][j] = Tile(True, self.tile_size, color)
                else:
                    matrix[i][j] = Tile(False, self.tile_size)

                matrix[i][j].matrix_pos = (i, j)

        return matrix

    def reset_matrix(self):
        for row in self.matrix:
            for tile in row:
                tile.revealed = False

    def get_tiles(self):
        tiles = []
        for row in self.matrix:
            for tile in row:
                tiles.append(tile)
        return tiles

    def get_transpose_matrix(self):
        transpose_cols_amount = self.rows_amount
        transpose_rows_amount = self.cols_amount
        transpose_matrix = [[0 for _ in range(transpose_cols_amount)] for _ in range(transpose_rows_amount)]

        for i, row in enumerate(self.matrix):
            for j, tile in enumerate(row):
                transpose_matrix[j][i] = self.matrix[i][j]

        return transpose_matrix

    def get_rows_numbers(self):
        rows_numbers = [[] for _ in range(self.rows_amount)]

        for i, row in enumerate(self.matrix):

            row_numbers = []
            consecutive_correct_tiles = 0

            for j, tile in enumerate(row):

                if self.matrix[i][j].correct:
                    consecutive_correct_tiles += 1

                elif consecutive_correct_tiles:
                    row_numbers.append(consecutive_correct_tiles)
                    consecutive_correct_tiles = 0

            if consecutive_correct_tiles:
                row_numbers.append(consecutive_correct_tiles)

            if row_numbers:
                rows_numbers[i] = row_numbers
            else:
                rows_numbers[i] = [0]

        return rows_numbers

    def get_cols_numbers(self):
        cols_numbers = [[] for _ in range(self.cols_amount)]
        transpose_matrix = self.get_transpose_matrix()

        for i, row in enumerate(transpose_matrix):

            col_numbers = []
            consecutive_correct_tiles = 0

            for j, tile in enumerate(row):

                if transpose_matrix[i][j].correct:
                    consecutive_correct_tiles += 1

                elif consecutive_correct_tiles:
                    col_numbers.append(consecutive_correct_tiles)
                    consecutive_correct_tiles = 0

            if consecutive_correct_tiles:
                col_numbers.append(consecutive_correct_tiles)

            if col_numbers:
                cols_numbers[i] = col_numbers
            else:
                cols_numbers[i] = [0]

        return cols_numbers

    def build_grid(self):
        for tile in self.tiles:
            tile.image.fill(Tile.unrevealed_color)
            tile.draw_border((Level.border[0] / 2, Level.border[1]))
            x, y = tile.matrix_pos
            tile.rect.topleft = (y * self.tile_size, x * self.tile_size)
            self.image.blit(tile.image, tile.rect)

    def test_for_completion(self):
        for tile in self.tiles:
            if tile.correct and not tile.revealed:
                return False

        for row in self.matrix:
            for tile in row:
                if tile.correct:
                    tile.image.fill(tile.color)
                else:
                    tile.image.fill(GRAY)

                self.image.blit(tile.image, tile.rect)

        return True

    def update_grid(self):
        for tile in self.tiles:
            if tile.correct and tile.revealed:
                tile.image.fill(Tile.revealed_color)
                self.image.blit(tile.image, tile.rect)

    def build_rows_numbers(self, rows_numbers):
        subrect = pygame.Rect((0, 0), (0, 0))
        subrect.height = rows_numbers.rect.height / self.rows_amount
        subrect.width = rows_numbers.rect.width

        number_font = Font(Font.pixelated, 30)

        for i in range(self.rows_amount):
            subrect.top = i * self.tile_size
            row = Sprite(rows_numbers.image.subsurface(subrect))
            row.draw_border((3, BLACK))

            for j, number in enumerate(reversed(self.rows_numbers[i])):
                number_subrect = pygame.Rect((0, 0), (28, subrect.height))
                number_subrect.left = subrect.width - number_subrect.width * (j + 1) - 20 * (j + 1)
                number_spr = Sprite(row.image.subsurface(number_subrect))
                number_font.center_write(str(number), WHITE, number_spr, number_spr.half_size)

    def build_cols_numbers(self, cols_numbers):
        subrect = pygame.Rect((0, 0), (0, 0))
        subrect.width = cols_numbers.rect.width / self.cols_amount
        subrect.height = cols_numbers.rect.height

        number_font = Font(Font.pixelated, 30)

        for i in range(self.cols_amount):
            subrect.left = i * self.tile_size
            col = Sprite(cols_numbers.image.subsurface(subrect))
            col.draw_border((3, BLACK))

            for j, number in enumerate(reversed(self.cols_numbers[i])):
                number_subrect = pygame.Rect((0, 0), (subrect.width, 28))
                number_subrect.top = subrect.height - number_subrect.height * (j + 1) - 20 * (j + 1)
                number_spr = Sprite(col.image.subsurface(number_subrect))
                number_font.center_write(str(number), WHITE, number_spr, number_spr.half_size)

    def build_level(self):
        self.reset_matrix()

        subrect = pygame.Rect((0, 0), (Screen.width - 130, Screen.height - 50))
        subrect.center = Screen.half_size
        picross = Sprite(Screen.window.subsurface(subrect))

        subrect.top = picross.rect.height - self.rect.height
        subrect.left = picross.rect.width - self.rect.width
        subrect.size = self.image.get_size()
        self.image = picross.image.subsurface(subrect)

        self.build_grid()
        self.rect.top = picross.rect.height - self.rect.height
        self.rect.left = picross.rect.width - self.rect.width

        subrect.top = 0
        subrect.left = self.rect.left
        subrect.height = picross.rect.height - self.rect.height
        subrect.width = self.rect.width
        cols_numbers = Sprite(picross.image.subsurface(subrect))
        self.build_cols_numbers(cols_numbers)

        subrect.left = 0
        subrect.top = self.rect.top
        subrect.width = picross.rect.width - self.rect.width
        subrect.height = self.rect.height
        rows_numbers = Sprite(picross.image.subsurface(subrect))
        self.build_rows_numbers(rows_numbers)

        subrect.topleft = (0, 0)
        subrect.width = picross.rect.width - self.rect.width
        subrect.height = picross.rect.height - self.rect.height
        level_info = Sprite(picross.image.subsurface(subrect))
        level_info_font = Font(Font.pixelated, 60)
        level_info_font.center_write(f'Fase  {self.number}', WHITE, level_info, level_info.half_size)

        errors_font = Font(Font.pixelated, 30)
        errors_font.center_write('Erros: 0', WHITE, level_info, (level_info.half_width, level_info.half_height + level_info_font.size))

        return Sprite(self.image), level_info, self.number

Y = YELLOW
L = LIGHT_BLUE
R = RED
P = PINK
O = ORANGE
B = BLUE
W = WHITE
N = BROWN
G = GREEN

lvl_1 = Level(50, [
    [0, Y, 0, Y, 0],
    [0, Y, 0, Y, 0],
    [0, 0, 0, 0, 0],
    [Y, 0, 0, 0, Y],
    [0, Y, Y, Y, 0]
])

lvl_2 = Level(50, [
    [0, R, R, R, 0],
    [R, R, R, R, R],
    [0, 0, L, 0, 0],
    [0, 0, L, 0, 0],
    [0, L, L, 0, 0]
])

lvl_3 = Level(50, [
    [0, P, P, P, 0],
    [P, 0, P, 0, P],
    [P, 0, P, 0, P],
    [P, P, 0, 0, P],
    [0, 0, 0, P, 0]
])

lvl_4 = Level(50, [
    [0, 0, R, 0, 0],
    [0, R, R, R, 0],
    [R, R, R, R, R],
    [0, W, 0, W, 0],
    [0, W, W, W, 0]
])

lvl_5 = Level(50, [
    [0, 0, 0, N, 0, 0, 0],
    [0, 0, N, 0, N, 0, 0],
    [0, N, N, N, N, N, 0],
    [N, N, N, 0, N, N, N],
    [0, N, N, N, N, N, 0],
    [0, 0, N, 0, N, 0, 0],
    [0, 0, 0, N, 0, 0, 0]
])

lvl_6 = Level(40, [
    [0, 0, 0, L, L, 0, 0, 0, 0, 0],
    [L, L, 0, 0, L, L, L, 0, 0, 0],
    [0, L, 0, 0, 0, L, L, 0, 0, 0],
    [0, L, L, 0, Y, Y, Y, Y, 0, 0],
    [0, 0, L, Y, Y, Y, Y, Y, Y, 0],
    [0, 0, L, Y, Y, Y, Y, 0, Y, Y],
    [0, L, L, Y, Y, Y, Y, Y, Y, Y],
    [0, L, L, 0, Y, Y, Y, Y, Y, 0],
    [L, L, 0, 0, 0, L, L, 0, 0, 0],
    [0, 0, 0, 0, L, L, 0, 0, 0, 0]
])

lvl_7 = Level(40, [
    [0, 0, 0, Y, Y, 0, 0, 0, 0, 0],
    [0, 0, Y, Y, Y, Y, 0, 0, 0, 0],
    [0, O, Y, 0, Y, Y, 0, 0, 0, 0],
    [O, 0, Y, Y, Y, Y, Y, 0, 0, 0],
    [0, O, Y, Y, Y, Y, Y, Y, Y, 0],
    [0, 0, Y, Y, Y, Y, Y, Y, Y, 0],
    [0, 0, Y, Y, Y, Y, Y, Y, Y, Y],
    [0, 0, 0, O, Y, Y, Y, Y, Y, Y],
    [0, 0, 0, O, 0, O, 0, Y, Y, 0],
    [0, 0, O, O, O, O, 0, 0, 0, 0]
])

lvl_8 = Level(40, [
    [0, N, N, N, N, 0, 0, N, 0, 0],
    [N, N, 0, N, N, 0, N, N, N, 0],
    [N, 0, 0, N, N, 0, N, 0, N, N],
    [0, 0, N, N, N, 0, N, N, N, N],
    [0, N, N, N, 0, N, N, N, N, 0],
    [0, N, N, 0, N, N, N, N, N, 0],
    [N, N, N, N, N, N, N, N, N, N],
    [0, N, N, N, N, N, N, N, 0, 0],
    [0, 0, 0, N, N, N, N, 0, 0, 0],
    [0, 0, 0, 0, N, N, N, N, N, 0]
])

lvl_9 = Level(40, [
    [0, 0, O, 0, O, 0, 0, 0, 0, 0],
    [0, O, O, O, O, 0, 0, 0, 0, 0],
    [O, 0, O, O, O, 0, 0, 0, O, 0],
    [O, O, O, O, O, 0, 0, O, 0, 0],
    [0, O, O, O, 0, 0, 0, O, O, 0],
    [0, 0, O, O, O, O, 0, 0, O, O],
    [0, 0, O, O, O, O, O, 0, 0, O],
    [0, O, O, O, O, O, O, 0, 0, O],
    [0, O, O, 0, O, O, O, 0, O, O],
    [O, O, 0, O, O, O, O, O, O, 0]
])

lvl_10 = Level(30, [
    [W, W, W, 0, R, R, R, 0, Y, Y, Y, 0, L, L, L, 0, G, G, G],
    [W, 0, 0, 0, R, 0, R, 0, 0, Y, 0, 0, L, 0, 0, 0, G, 0, 0],
    [W, W, 0, 0, R, R, R, 0, 0, Y, 0, 0, L, L, 0, 0, G, 0, 0],
    [W, 0, 0, 0, R, 0, R, 0, 0, Y, 0, 0, L, 0, 0, 0, G, 0, 0],
    [W, 0, 0, 0, R, 0, R, 0, 0, Y, 0, 0, L, L, L, 0, G, G, G]
])
