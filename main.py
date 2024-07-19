import sys
import pygame
from constants import *
from basis import Sprite, Font, Screen, Level


def picross(level):

    # Function to build the interface and return what's necessary to have control over what's being clicked
    def build():
        Screen.window.fill(GRAY)
        Screen.draw_return_msg()
        return level.build_level()

    level_grid, level_info, level_number = build()

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                level_selection()

        pygame.display.flip()

    pygame.quit()
    sys.exit()



def level_selection():

    def build():

        Screen.window.fill(GRAY)
        Screen.draw_return_msg()
        pygame.display.set_caption(CAPTION_TITLE + 'Seleção de Fases')
        title_font = Font('assets/pixelated.ttf', 80)

        def main():
            subrect = pygame.Rect((0, 0), (Screen.width - 200, Screen.height - 50))
            subrect.center = Screen.half_size
            return Sprite(Screen.window.subsurface(subrect))

        main = main()
        title_font.center_write('Fases', WHITE, main, (main.half_width, title_font.size))

        def button_image():
            image = pygame.Surface((80, 80))
            image.fill(YELLOW)
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
                    button_font.center_write(str(level_count), BLACK, button, button.half_size)
                    button.rect.left = j * (button.rect.width + button_spacing)
                    button.rect.top = i * (button.rect.height + button_spacing)
                    button.draw_border((3, BLACK))
                    button_container.image.blit(button.image, button.rect)
                    buttons.append(dict(level = level_count, sprite = button))
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
                        level_number = button['level'] - 1
                        chosen_level = Level.levels[level_number]
                        picross(chosen_level)

        pygame.display.flip()

    pygame.quit()
    sys.exit()



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

    pygame.quit()
    sys.exit()



def menu():

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
                        match button['action']:
                            case 'play': level_selection()
                            case 'tutorial': tutorial()
                            case 'quit': running = False
                        break

        pygame.display.flip()

    pygame.quit()
    sys.exit()



if __name__ == '__main__':
    pygame.init()
    menu()