import pygame
from auxiliary import *


class Sprite(pygame.sprite.Sprite):

    def __init__(self, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.size = (self.width, self.height)
        self.half_width = self.width / 2
        self.half_height = self.height / 2
        self.half_size = (self.half_width, self.half_height)

    def draw_border(self, border):
        bt = border[0] # Border thickness
        hbt = bt / 2 # Half border thickness
        bc = border[1] # Border color

        topleft = (0 - hbt,) * 2
        bottomleft = (0 - hbt, self.height - hbt)
        topright = (self.width - hbt, 0 - hbt)
        horizontal = (self.width + bt, bt)
        vertical = (bt, self.height + bt)

        pygame.draw.rect(self.image, bc, topleft + horizontal)
        pygame.draw.rect(self.image, bc, bottomleft + horizontal)
        pygame.draw.rect(self.image, bc, topleft + vertical)
        pygame.draw.rect(self.image, bc, topright + vertical)


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
            Sfx.ding.play()
            self.revealed = True
            self.image.fill(Tile.revealed_color)

    def mark_wrong(self, left_click = False):
        if self.revealed: return
        Sfx.woosh.play()
        if self.marked_wrong and not left_click: # Unmark as wrong
            pygame.draw.line(self.image, Tile.unrevealed_color, (0, 0), (self.rect.width, self.rect.height))
            pygame.draw.line(self.image, Tile.unrevealed_color, (self.rect.width, 0), (0, self.rect.height))
            self.draw_border((3, BLACK))
            self.marked_wrong = False
        elif not self.marked_wrong: # Mark as wrong
            pygame.draw.line(self.image, BLACK, (0, 0), (self.rect.width, self.rect.height))
            pygame.draw.line(self.image, BLACK, (self.rect.width, 0), (0, self.rect.height))
            self.marked_wrong = True



pygame.mixer.init()

class Music:

    enabled = True
    loaded_track = None
    menu = 'assets/menu.mp3'
    level_solved = 'assets/level_solved.mp3'
    level_tracks = [f'assets/level_{i}.mp3' for i in range(1, 5)]
    current_level_track = 0

    @classmethod
    def play(cls, music, loops = -1):
        if cls.loaded_track != music and cls.enabled:
            cls.loaded_track = music
            pygame.mixer.music.load(music)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(loops)

    @classmethod
    def play_level_track(cls):
        if cls.current_level_track == len(cls.level_tracks) - 1:
            cls.current_level_track = 0
        else:
            cls.current_level_track += 1

        cls.play(cls.level_tracks[cls.current_level_track])

    @classmethod
    def toggle(cls):
        cls.enabled = not cls.enabled

        if cls.enabled:
            cls.play(Music.menu)
        else:
            cls.loaded_track = None
            pygame.mixer.music.unload()



class Sfx:

    volume = 5
    woosh = pygame.mixer.Sound('assets/se_06.wav')
    ding = pygame.mixer.Sound('assets/se_09.wav')
    all = [woosh, ding]

    @classmethod
    def set_volume(cls, volume):
        if volume >= 0 and volume <= 10:
            cls.volume = volume
            volume /= 10
            for sound in cls.all:
                sound.set_volume(volume)

Sfx.set_volume(Sfx.volume)



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

        self.info = None # This will later become a sprite to display the level number and error count

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
                tile.marked_wrong = False

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

            for tile in row:

                if tile.correct:
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

            for tile in row:

                if tile.correct:
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

        return True

    def complete(self):
        self.reveal_grid()
        Music.play(Music.level_solved, 0)

    def reveal_grid(self):
        for row in self.matrix:
            for tile in row:
                if tile.correct:
                    tile.image.fill(tile.color)
                else:
                    tile.image.fill(GRAY)

                self.image.blit(tile.image, tile.rect)

    def update_grid(self):
        for tile in self.tiles:
            if tile.correct and tile.revealed:
                tile.image.fill(Tile.revealed_color)

            self.image.blit(tile.image, tile.rect)

    def build_rows_numbers(self, rows_numbers):
        subrect = pygame.Rect(0, 0, 0, 0)
        subrect.height = rows_numbers.rect.height / self.rows_amount
        subrect.width = rows_numbers.rect.width

        number_font = Font(Font.pixelated, 30)

        for i in range(self.rows_amount):
            subrect.top = i * self.tile_size
            row = Sprite(rows_numbers.image.subsurface(subrect))
            row.draw_border((3, BLACK))

            for j, number in enumerate(self.rows_numbers[i][::-1]):
                number_subrect = pygame.Rect((0, 0), (28, subrect.height))
                number_subrect.left = subrect.width - number_subrect.width * (j + 1) - 20 * (j + 1)
                number_spr = Sprite(row.image.subsurface(number_subrect))
                number_font.center_write(str(number), WHITE, number_spr, number_spr.half_size)

    def build_cols_numbers(self, cols_numbers):
        subrect = pygame.Rect(0, 0, 0, 0)
        subrect.width = cols_numbers.rect.width / self.cols_amount
        subrect.height = cols_numbers.rect.height

        number_font = Font(Font.pixelated, 30)

        for i in range(self.cols_amount):
            subrect.left = i * self.tile_size
            col = Sprite(cols_numbers.image.subsurface(subrect))
            col.draw_border((3, BLACK))

            for j, number in enumerate(self.cols_numbers[i][::-1]):
                number_subrect = pygame.Rect((0, 0), (subrect.width, 28))
                number_subrect.top = subrect.height - number_subrect.height * (j + 1) - 20 * (j + 1)
                number_spr = Sprite(col.image.subsurface(number_subrect))
                number_font.center_write(str(number), WHITE, number_spr, number_spr.half_size)

    def build(self):
        self.reset_matrix()

        subrect = pygame.Rect((0, 0), (Screen.width - 130, Screen.height - 50))

        def picross():
            subrect.center = Screen.half_size
            return Sprite(Screen.window.subsurface(subrect))

        picross = picross()

        def image():
            subrect.top = picross.rect.height - self.rect.height
            subrect.left = picross.rect.width - self.rect.width
            subrect.size = self.image.get_size()
            return picross.image.subsurface(subrect)

        self.image = image()

        self.build_grid()
        self.rect.top = picross.rect.height - self.rect.height
        self.rect.left = picross.rect.width - self.rect.width


        def cols_numbers():
            subrect.top = 0
            subrect.left = self.rect.left
            subrect.height = picross.rect.height - self.rect.height
            subrect.width = self.rect.width
            return Sprite(picross.image.subsurface(subrect))

        cols_numbers = cols_numbers()
        self.build_cols_numbers(cols_numbers)

        def rows_numbers():
            subrect.left = 0
            subrect.top = self.rect.top
            subrect.width = picross.rect.width - self.rect.width
            subrect.height = self.rect.height
            return Sprite(picross.image.subsurface(subrect))

        rows_numbers = rows_numbers()
        self.build_rows_numbers(rows_numbers)

        def info():
            subrect.topleft = (0, 0)
            subrect.width = picross.rect.width - self.rect.width
            subrect.height = picross.rect.height - self.rect.height
            return Sprite(picross.image.subsurface(subrect))

        self.info = info()
        self.info_font = Font(Font.pixelated, 60)
        self.info_font.center_write(f'Fase  {self.number}', WHITE, self.info, self.info.half_size)

        errors_font = Font(Font.pixelated, 30)
        errors_font.center_write('Erros: 0', WHITE, self.info, (self.info.half_width, self.info.half_height + self.info_font.size))

        return Sprite(self.image), self.info

    def update_info(self, error_count):
        self.info.image.fill(GRAY)

        self.info_font = Font(Font.pixelated, 60)
        self.info_font.center_write(f'Fase  {self.number}', WHITE, self.info,
                                     self.info.half_size)

        error_font = Font(Font.pixelated, 30)
        error_font.center_write(f'Erros: {error_count}', WHITE, self.info, (
            self.info.half_width, self.info.half_height + self.info_font.size))


K = BLACK
Y = YELLOW
L = LIGHT_BLUE
R = RED
P = PINK
O = ORANGE
B = BLUE
W = WHITE
N = BROWN
Q = QUANTUM
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
    [0, 0, 0, G, 0, 0, 0],
    [0, 0, Y, 0, Y, 0, 0],
    [0, Y, G, G, G, Y, 0],
    [G, Y, G, 0, G, Y, G],
    [0, Y, G, G, G, Y, 0],
    [0, 0, Y, 0, Y, 0, 0],
    [0, 0, 0, G, 0, 0, 0]
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
    [N, 0, 0, N, N, 0, N, 0, N, Q],
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
    [O, 0, O, O, O, 0, 0, 0, W, 0],
    [O, O, O, O, O, 0, 0, W, 0, 0],
    [0, O, O, O, 0, 0, 0, O, O, 0],
    [0, 0, O, O, O, O, 0, 0, O, O],
    [0, 0, O, O, O, O, O, 0, 0, O],
    [0, O, O, O, O, O, O, 0, 0, O],
    [0, O, O, 0, O, O, O, 0, O, O],
    [W, O, 0, W, O, O, O, O, O, 0]
])

lvl_10 = Level(27, [
    [O, 0, 0, 0, R, R, R, 0, Y, Y, Y, 0, L, L, L, 0, G, 0, 0],
    [O, 0, 0, 0, R, 0, 0, 0, Y, 0, 0, 0, L, 0, L, 0, G, 0, 0],
    [O, 0, 0, 0, R, R, 0, 0, Y, 0, Y, 0, L, L, L, 0, G, 0, 0],
    [O, 0, 0, 0, R, 0, 0, 0, Y, 0, Y, 0, L, 0, L, 0, G, 0, 0],
    [O, O, O, 0, R, R, R, 0, Y, Y, Y, 0, L, 0, L, 0, G, G, G]
])
