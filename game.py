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


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[1] * width for _ in range(height)]
        self.left = 100
        self.top = 10
        self.cell_size = 30

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(Screen, pygame.Color(255, 100, 100), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size, self.cell_size),
                                 self.board[y][x])

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def on_click(self, cell_coords):
        self.board[cell_coords[0]][cell_coords[1]] = (self.board[cell_coords[0]][cell_coords[1]] + 1) % 2

    def get_cell(self, mouse_pos):
        if self.left <= mouse_pos[1] < self.left + self.height * self.cell_size\
                and self.top <= mouse_pos[0] < self.top + self.width * self.cell_size:
            return int((mouse_pos[1] - self.left) / self.cell_size), int((mouse_pos[0] - self.top) / self.cell_size)
        else:
            return None

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            self.on_click(cell)



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


def game(diff):
    if diff == 0:
        board = Board(4, 4)
        board.set_view(100, 100, 50)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    board.get_click(event.pos)
            Screen.fill((100, 100, 100))
            board.render()
            pygame.display.flip()
        pygame.quit()
    if diff == 1:
        board = Board(6, 6)
        board.set_view(100, 100, 50)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    board.get_click(event.pos)
            Screen.fill((100, 100, 100))
            board.render()
            pygame.display.flip()
        pygame.quit()


start_screen()

ACTUALL_DIFF = None


def main():
    mousex = 0
    mousey = 0
    pygame.display.set_caption('MEMory Game')
    first_box = None  # ЕГОР, СЮДА ТЫ ПИХАЕШЬ КОРБКУ, НА КОТОРУЮ НАЖАЛИ В ПЕРВЫЙ РАЗ
    Screen.fill(BGCOLOR)
    running = True
    while running:

        def set_difficulty(value, difficulty):
            global ACTUALL_DIFF
            ACTUALL_DIFF = value[1]
            return ACTUALL_DIFF

        def start_the_game():
            diff = ACTUALL_DIFF
            game(diff)

        menu = pygame_menu.Menu('Добро пожаловать', 800, 600,
                                theme=pygame_menu.themes.THEME_DEFAULT)

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