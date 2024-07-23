import sys
import pygame
import json
from constants import *
from basis import Sprite, Font, Screen, Level, Music, SFX

def get_progress():
    with open(PROGRESS_FILE, 'r') as file:
        return json.load(file)

def save_progress(new_info):
    with open(PROGRESS_FILE, 'w') as file:
        json.dump(new_info, file, indent = 4)

pgs = get_progress()

def quit():
    save_progress(pgs)
    pygame.quit()
    sys.exit()



def picross(level):

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

        rows = 2
        cols = 5

        def button_container():
            subrect = pygame.Rect((0, 0),
                                  (button_rect.width * cols + (cols - 1) * button_spacing,
                                   button_rect.height * rows + button_spacing))
            subrect.center = (main.half_width, main.half_height + 50)
            return Sprite(main.image.subsurface(subrect))

        button_container = button_container()

        def buttons():
            level_count = 1
            buttons = []

            for i in range(rows):
                for j in range(cols):
                    button = Sprite(button_image())

                    if pgs[level_count - 1]['unlocked']:
                        button.image.fill(YELLOW)
                        buttons.append(dict(level = level_count, sprite = button))

                    button_font.center_write(str(level_count), BLACK, button, button.half_size)
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
                        level_number = button['level'] - 1
                        chosen_level = Level.levels[level_number]
                        picross(chosen_level)
                        break

        pygame.display.flip()

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

    quit()



if __name__ == '__main__':
    pygame.init()
    menu()