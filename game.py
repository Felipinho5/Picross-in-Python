import sys
import pygame
import json
import math
from constants import *
from basis import Sprite, Font, Screen, Level, Music, SFX

pgs = None
clock = pygame.time.Clock()

def load_progress():
    global pgs

    with open(PROGRESS_FILE, 'r') as file:
        pgs = json.load(file)

def save_progress():
    global pgs

    with open(PROGRESS_FILE, 'w') as file:
        json.dump(pgs, file, indent = 4)

def reset_progress():
    global pgs

    with open(PROGRESS_RESET_FILE, 'r') as source:
        reset_pgs = json.load(source)

    with open(PROGRESS_FILE, 'w') as target:
        json.dump(reset_pgs, target, indent = 4)

    pgs = reset_pgs

def quit():
    save_progress()
    pygame.quit()
    sys.exit()



def picross(level):
    global pgs

    Music.play_level_track()

    # Function to build the interface and return what's necessary to have control over what's being clicked
    def build():
        Screen.window.fill(GRAY)
        Screen.draw_return_msg()
        pygame.display.set_caption(CAPTION_TITLE + f'Fase {level.number}')
        return level.build()

    level_grid, level_info = build()
    level_completed = False
    error_count = 0

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                level_selection()

            if event.type == pygame.MOUSEBUTTONDOWN and not level_completed:
                mouse_pos = tuple(a - b for a, b in zip(pygame.mouse.get_pos(), level_grid.image.get_abs_offset()))

                for tile in level.tiles:
                    if tile.rect.collidepoint(mouse_pos):
                        if event.button == 1: # Left click
                            if tile.correct:
                                tile.reveal()
                            else:
                                tile.mark_wrong(True)

                                if error_count < 999:
                                    error_count += 1
                                    level.update_info(error_count)

                        elif event.button == 3: # Right click
                            tile.mark_wrong()

                        level.update_grid()

                        if level.test_for_completion():
                            level.complete()

                            this_level = pgs[level.number - 1]

                            this_level['completed'] = level_completed = True

                            if this_level['fewest_errors'] is None or this_level['fewest_errors'] > error_count:
                                this_level['fewest_errors'] = error_count

                            if level.number < len(pgs):
                                pgs[level.number]['unlocked'] = True

                            error_count = 0

                        break

        pygame.display.flip()

    quit()



def level_selection():
    global pgs

    Music.play(Music.menu)

    def build():

        Screen.window.fill(GRAY)
        Screen.draw_return_msg()
        pygame.display.set_caption(CAPTION_TITLE + 'Seleção de Fases')
        title_font = Font(Font.pixelated, 80)

        def main():
            subrect = pygame.Rect((0, 0), (Screen.width - 200, Screen.height - 50))
            subrect.center = Screen.half_size
            return Sprite(Screen.window.subsurface(subrect))

        main = main()
        title_font.center_write('Fases', WHITE, main, (main.half_width, title_font.size))

        def button_image():
            image = pygame.Surface((80, 80))
            image.fill(LIGHT_BLUE)
            return image

        button_rect = button_image().get_rect()
        button_spacing = 20
        button_font = Font(Font.pixelated, 30)
        record_font = Font(Font.pixelated, 16)

        rows = 2
        cols = 5

        def button_container():
            subrect = pygame.Rect((0, 0),
                                  (button_rect.width * cols + (cols - 1) * button_spacing,
                                   button_rect.height * rows + button_spacing + 170))
            subrect.center = (main.half_width, main.half_height + 50)
            return Sprite(main.image.subsurface(subrect))

        button_container = button_container()

        def buttons():
            level_count = 1
            buttons = []

            def draw_checkmark(target_spr):

                line_width = 5

                line_start_1 = (5, target_spr.height / 2)
                line_end_1 = (target_spr.width / 2 - 3, target_spr.width - 5)
                pygame.draw.line(target_spr.image, GREEN, line_start_1, line_end_1, line_width)

                line_end_2 = (target_spr.width - 8, 5)
                pygame.draw.line(target_spr.image, GREEN, line_end_1, line_end_2, line_width)

            def draw_star(target_spr):
                margin = 5
                w, h = target_spr.size
                star_size = min(w, h) - 2 * margin
                center = (w / 2, h / 2)
                num_points = 5

                # Calculate the positions of the points
                points = []
                for i in range(num_points * 2):
                    angle = i * math.pi / num_points
                    if i % 2 == 0:
                        r = star_size / 2
                    else:
                        r = star_size / 4
                    x = center[0] + r * math.cos(angle)
                    y = center[1] + r * math.sin(angle)
                    points.append((x, y))

                # Draw the star
                pygame.draw.polygon(target_spr.image, GREEN, points)

            def topright_corner(target_spr):
                subrect = pygame.Rect(0, 0, 0, 0)
                subrect.size = (30,) * 2
                subrect.topleft = (target_spr.width - subrect.width, 0)
                return Sprite(target_spr.image.subsurface(subrect))

            def build_reset_progress_button():
                reset_progress_button = Sprite(pygame.Surface((button_container.width, button_image().get_height())))
                reset_progress_button.image.fill(YELLOW)
                reset_progress_button.rect.bottomright = button_container.size
                reset_progress_button.draw_border((3, BLACK))

                reset_progress_font = Font(Font.pixelated, 30)
                reset_progress_font.center_write('Zerar progresso', BLACK, reset_progress_button, reset_progress_button.half_size)

                buttons.append(dict(level = -1, sprite = reset_progress_button))
                button_container.image.blit(reset_progress_button.image, reset_progress_button.rect)

            build_reset_progress_button()

            for i in range(rows):
                for j in range(cols):
                    button = Sprite(button_image())

                    this_level = pgs[level_count - 1]
                    corner = topright_corner(button)

                    if this_level['unlocked']:
                        button.image.fill(YELLOW)
                        buttons.append(dict(level = level_count, sprite = button))

                        if this_level['completed']:
                            record_font.topleft_write(
                                'Recorde:',
                                BLACK, button, (5, button.height - record_font.size * 2)
                            )

                            plural = '' if this_level['fewest_errors'] == 1 else 's'

                            record_font.topleft_write(
                                f'{this_level['fewest_errors']} erro{plural}',
                                BLACK, button, (5, button.height - record_font.size)
                            )

                            if this_level['fewest_errors'] == 0:
                                draw_star(corner)
                            else:
                                draw_checkmark(corner)

                    button_font.topleft_write(str(level_count), BLACK, button, (5, 5))
                    button.rect.left = j * (button.rect.width + button_spacing)
                    button.rect.top = i * (button.rect.height + button_spacing)
                    button.draw_border((3, BLACK))
                    button_container.image.blit(button.image, button.rect)
                    level_count += 1

            return buttons

        buttons = buttons()

        return button_container, buttons



    button_container, buttons = build()

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = tuple(a - b for a, b in zip(pygame.mouse.get_pos(), button_container.image.get_abs_offset()))

                for button in buttons:
                    if button['sprite'].rect.collidepoint(mouse_pos):
                        SFX['ding'].play()
                        if button['level'] == -1: # Reset progress button
                            reset_progress()
                            level_selection()
                        else:
                            level_number = button['level'] - 1
                            chosen_level = Level.levels[level_number]
                            picross(chosen_level)
                        break

        pygame.display.flip()
        clock.tick(30)

    quit()



def tutorial():

    # Function to build the interface and return what's necessary to have control over what's being clicked
    def build():

        Screen.window.fill(GRAY)
        Screen.draw_return_msg()
        pygame.display.set_caption(CAPTION_TITLE + 'Tutorial')

        tutorial = Sprite(pygame.image.load('assets/picross_tutorial.png'))
        tutorial.rect.center = Screen.half_size
        Screen.window.blit(tutorial.image, tutorial.rect)



    build()

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu()

        pygame.display.flip()
        clock.tick(30)

    quit()


def menu():

    Music.play(Music.menu)

    # Function to build the interface and return what's necessary to have control over what's being clicked
    def build():

        Screen.window.fill(GRAY)
        pygame.display.set_caption(CAPTION_TITLE + 'Menu')
        title_font = Font(Font.pixelated, 80)

        def main():
            subrect = pygame.Rect((0, 0), (Screen.width / 2, Screen.height - 50))
            subrect.center = Screen.half_size
            return Sprite(Screen.window.subsurface(subrect))

        main = main()
        title_font.center_write('PICROSS', WHITE, main, (main.half_width, title_font.size))

        def button_image():
            image = pygame.Surface((300, 50))
            image.fill(YELLOW)
            return image

        button_rect = button_image().get_rect()
        button_spacing = 30
        button_font = Font(Font.pixelated, 30)

        def buttons():
            play_button = Sprite(button_image())
            button_font.center_write('Jogar', BLACK, play_button, play_button.half_size)

            tutorial_button = Sprite(button_image())
            button_font.center_write('Tutorial', BLACK, tutorial_button, tutorial_button.half_size)

            quit_button = Sprite(button_image())
            button_font.center_write('Sair', BLACK, quit_button, quit_button.half_size)

            return [
                dict(action = 'play', sprite = play_button),
                dict(action = 'tutorial', sprite = tutorial_button),
                dict(action = 'quit', sprite = quit_button)
            ]

        buttons = buttons()
        button_amount = len(buttons)

        def button_container():
            subrect = pygame.Rect((0, 0),
                                  (button_rect.width,
                                   button_amount * button_rect.height + (button_amount - 1) * button_spacing))
            subrect.center = (main.half_width, main.half_height + 50)
            return Sprite(main.image.subsurface(subrect))

        button_container = button_container()

        for i, button in enumerate(buttons):
            spr = button['sprite']
            spr.rect.top = i * (button_rect.height + button_spacing)
            spr.draw_border((3, BLACK))
            button_container.image.blit(spr.image, spr.rect)

        return button_container, buttons



    button_container, buttons = build()

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = tuple(a - b for a, b in zip(pygame.mouse.get_pos(), button_container.image.get_abs_offset()))

                for button in buttons:
                    if button['sprite'].rect.collidepoint(mouse_pos):
                        SFX['ding'].play()
                        match button['action']:
                            case 'play': level_selection()
                            case 'tutorial': tutorial()
                            case 'quit': running = False
                        break

        pygame.display.flip()
        clock.tick(30)

    quit()

if __name__ == '__main__':
    load_progress()
    pygame.init()
    menu()