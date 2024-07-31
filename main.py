import sys
import pygame
import math
import asyncio
from auxiliary import *
from basis import Sprite, Font, Screen, Level, Music, Sfx

pygame.init()
clock = pygame.time.Clock()

async def update():
    pygame.display.flip()
    clock.tick(30)
    await asyncio.sleep(0)

def quit():
    pygame.quit()
    sys.exit()

def relative_mouse_pos(related_spr):
    return tuple(a - b for a, b in zip(pygame.mouse.get_pos(), related_spr.image.get_abs_offset()))



async def picross(level):
    pgs = load_progress()

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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                await level_selection()

            if event.type == pygame.MOUSEBUTTONDOWN and not level_completed:
                mouse_pos = relative_mouse_pos(level_grid)

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
                            save_progress(pgs)

                        break

        await update()

    quit()



async def level_selection():
    pgs = load_progress()

    Music.play(Music.menu)

    # Function to build the interface and return what's necessary to have control over what's being clicked
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
                reset_progress_button.draw_border(3, BLACK)

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
                    button.draw_border(3, BLACK)
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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                await main()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = relative_mouse_pos(button_container)

                for button in buttons:
                    if button['sprite'].rect.collidepoint(mouse_pos):
                        Sfx.ding.play()
                        if button['level'] == -1: # Reset progress button
                            pgs = reset_progress()
                            await level_selection()
                        else:
                            level_number = button['level'] - 1
                            chosen_level = Level.levels[level_number]
                            await picross(chosen_level)
                        break

        await update()

    quit()



async def options():

    # Function to build the interface and return what's necessary to have control over what's being clicked
    def build():
        Screen.window.fill(GRAY)
        Screen.draw_return_msg()
        pygame.display.set_caption(CAPTION_TITLE + 'Volume')

        def main():
            subrect = pygame.Rect(0, 0, 0, 0)
            subrect.size = (500, 550)
            subrect.center = Screen.half_size
            return Sprite(Screen.window.subsurface(subrect))

        main = main()
        title_font = Font(Font.pixelated, 80)
        title_font.center_write('Volume', WHITE, main, (main.half_width, title_font.size))

        def volume_setter(name, related_class, pos):

            def container():
                subrect = pygame.Rect(0, 0, 0, 0)
                subrect.size = (main.width, 100)
                subrect.center = pos
                return Sprite(main.image.subsurface(subrect))

            container = container()

            def draw_name(name):
                subrect = pygame.Rect(0, 0, 0, 0)
                subrect.size = (container.width, container.height / 2)
                name_spr = Sprite(container.image.subsurface(subrect))

                name_font = Font(Font.pixelated, 35)
                name_font.center_write(name, WHITE, name_spr, name_spr.half_size)

            draw_name(name)

            def setter():
                subrect = pygame.Rect(0, 0, 0, 0)
                subrect.size = (container.width, container.height / 2)
                subrect.bottomright = container.size
                return Sprite(container.image.subsurface(subrect))

            setter = setter()

            def draw_button(spr, text):
                spr.image.fill(YELLOW)
                spr.draw_border(3, BLACK)
                button_font = Font(Font.pixelated, 30)
                button_font.center_write(text, BLACK, spr, spr.half_size)
                setter.image.blit(spr.image, spr.rect)

            button_size = (setter.height,) * 2

            def minus_button():
                spr = Sprite(pygame.Surface(button_size))
                draw_button(spr, '-')
                return spr

            minus_button = minus_button()

            def plus_button():
                spr = Sprite(pygame.Surface(button_size))
                spr.rect.bottomright = setter.size
                draw_button(spr, '+')
                return spr

            plus_button = plus_button()

            def measurer():
                subrect = pygame.Rect(0, 0, 0, 0)
                w = button_size[0]
                subrect.width = setter.width - w * 2 - 40
                subrect.height = setter.height
                subrect.center = setter.half_size
                return Sprite(setter.image.subsurface(subrect))

            measurer = measurer()

            def measure_bars():
                bars = []
                bar_width = 18
                bar_amount = 10
                bar_spacing = (measurer.width - bar_width * 10) / (bar_amount - 1)

                for i in range(bar_amount):
                    subrect = pygame.Rect(0, 0, 0, 0)
                    subrect.size = (bar_width, measurer.height)
                    subrect.left = i * (bar_spacing + bar_width)
                    bar = Sprite(measurer.image.subsurface(subrect))
                    bars.append(bar)

                return bars

            measure_bars = measure_bars()

            return dict(
                minus_button = minus_button,
                plus_button = plus_button,
                measure_bars = measure_bars,
                setter = setter,
                related_class = related_class
            )

        def music_toggler():
            def container():
                subrect = pygame.Rect(0, 0, 0, 0)
                subrect.size = (main.width, 100)
                subrect.bottomright = (main.width, main.height - 50)
                return Sprite(main.image.subsurface(subrect))

            container = container()

            def draw_name():
                subrect = pygame.Rect(0, 0, 0, 0)
                subrect.size = (container.width, container.height / 2)
                name_spr = Sprite(container.image.subsurface(subrect))

                name_font = Font(Font.pixelated, 35)
                name_font.center_write('Faixas musicais', WHITE, name_spr, name_spr.half_size)

            draw_name()

            def toggle_button():
                subrect = pygame.Rect(0, 0, 0, 0)
                subrect.size = (container.width, container.height / 2)
                subrect.bottomright = container.size
                spr = Sprite(container.image.subsurface(subrect))
                spr.image.fill(YELLOW)
                spr.draw_border(3, BLACK)

                text_font = Font(Font.pixelated, 30)
                text_font.center_write('Ativar / Desativar', BLACK, spr, spr.half_size)
                return spr

            return toggle_button()

        music_toggler = music_toggler()

        return volume_setter('Efeitos sonoros', Sfx, main.half_size), music_toggler



    def update_volume_measurer(setter):
        for i, bar in enumerate(setter['measure_bars']):
            color = YELLOW if i < setter['related_class'].volume else LIGHT_BLUE
            bar.image.fill(color)
            bar.draw_border(3, BLACK)



    sfx_volume, music_toggler = build()
    update_volume_measurer(sfx_volume)

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                await main()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = relative_mouse_pos(sfx_volume['setter'])

                new_volume = Sfx.volume

                if sfx_volume['minus_button'].rect.collidepoint(mouse_pos): new_volume -= 1
                elif sfx_volume['plus_button'].rect.collidepoint(mouse_pos): new_volume += 1

                if new_volume != Sfx.volume:
                    Sfx.ding.play()
                    Sfx.set_volume(new_volume)
                    update_volume_measurer(sfx_volume)
                else:
                    mouse_pos = relative_mouse_pos(music_toggler)
                    if music_toggler.rect.collidepoint(mouse_pos):
                        Sfx.ding.play()
                        Music.toggle()

        await update()

    quit()



async def tutorial():

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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                await main()

        await update()

    quit()



async def main():

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

            options_button = Sprite(button_image())
            button_font.center_write('Volume', BLACK, options_button, options_button.half_size)

            return [
                dict(action = 'play', sprite = play_button),
                dict(action = 'tutorial', sprite = tutorial_button),
                dict(action = 'options', sprite = options_button),
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
            spr.draw_border(3, BLACK)
            button_container.image.blit(spr.image, spr.rect)

        return button_container, buttons



    button_container, buttons = build()

    running = True
    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = relative_mouse_pos(button_container)

                for button in buttons:
                    if button['sprite'].rect.collidepoint(mouse_pos):
                        Sfx.ding.play()
                        match button['action']:
                            case 'play': await level_selection()
                            case 'tutorial': await tutorial()
                            case 'options': await options()
                        break

        await update()

    quit()


asyncio.run(main())