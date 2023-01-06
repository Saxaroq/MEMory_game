import os
import pygame
import sys
import pygame_menu

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
BOX_SIZE = 30
BETWEEN_BOX = 15

BGCOLOR = pygame.Color("BLUE")
BOXCOLOT = pygame.Color("WHITE")

Screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
clock = pygame.time.Clock()

pygame.init()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["MEMory game", "",
                  "Правила игры:",
                  "После нажатия на любую клавишу вы увидите поле из кратинок",
                  "У вас есть три секунды, чтобы запомнить их положние",
                  "После чего они закроются и вам нужно будет их открыть по памяти", "",
                  "Сейчас вы увидете меню, в котором сможете выбрать сложность игры и ввести свое имя", "",
                  "Удачи!"]
    back_screen = pygame.transform.scale(load_image('background_image.jpg'), (WINDOWWIDTH, WINDOWHEIGHT))
    Screen.blit(back_screen, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        Screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()


def main():
    mousex = 0
    mousey = 0
    pygame.display.set_caption('MEMory Game')
    first_box = None  # ЕГОР, СЮДА ТЫ ПИХАЕШЬ КОРБКУ, НА КОТОРУЮ НАЖАЛИ В ПЕРВЫЙ РАЗ
    Screen.fill(BGCOLOR)
    running = True

    while running:

        def set_difficulty(value, difficulty):
            pass

        def start_the_game():
            pass

        menu = pygame_menu.Menu('Добро пожаловать', 800, 600,
                                theme=pygame_menu.themes.THEME_BLUE)

        menu.add.text_input('Ваше имя :', default='Jo Mama')
        menu.add.selector('Сложность :', [('Легкая', 1), ('Сложная', 2)], onchange=set_difficulty)
        menu.add.button('Играть', start_the_game)
        menu.add.button('Выйти', pygame_menu.events.EXIT)

        menu.mainloop(Screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == '__main__':
    main()