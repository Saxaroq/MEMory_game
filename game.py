import os
import pygame
import sys
import pygame_menu
import sqlite3
import time

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
RESULT = 10000
COORDS = []
COUNTER = 0
HARD_COUNTER = 0
NAME = 'User'

Screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
WinScreen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
pygame.init()


# ниже прописан цикл загрузки картинок (для того, чтобы не копаться в дате и путься os)
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


# ниже прописан класс для обработки сохранения спрайтов и их гифок
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.iter = 0
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.iter += 1
        if self.iter % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


# анимированные монетки, которые сохраняются при помощи выше описаной функции

coin1 = AnimatedSprite(load_image("coin2_20x20.png"), 9, 1, 100, 100)
coin2 = AnimatedSprite(load_image("coin2_20x20.png"), 9, 1, 700, 100)
coin3 = AnimatedSprite(load_image("coin2_20x20.png"), 9, 1, 100, 400)
coin4 = AnimatedSprite(load_image("coin2_20x20.png"), 9, 1, 700, 400)

# класс для доски, ресующей поля для игры


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[1] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 64

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

    def get_cell(self, mouse_pos):
        global COORDS
        board_width = self.width * self.cell_size
        board_height = self.height * self.cell_size
        if self.left < mouse_pos[0] < self.left + board_width:
            if self.top < mouse_pos[1] < self.top + board_height:
                cell_coords = (mouse_pos[1] - self.left) // self.cell_size, \
                              (mouse_pos[0] - self.top) // self.cell_size
                print(cell_coords)
                return cell_coords

    def on_click(self, cell_coords):
        i = cell_coords[0]
        j = cell_coords[1]
        if (i >= 0 and j >= 0) and (i < self.width and j < self.height):
            i = cell_coords[0]
            j = cell_coords[1]
            return i, j

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            self.on_click(cell)
            return cell


# функция экстренного сворачивания (на всякий случай)
def terminate():
    pygame.quit()
    sys.exit()

# функция сохранения результата и имени в бд


def save_bd():
    global RESULT, NAME
    if NAME == 'User':
        NAME = 'NoName'
    try:
        sqlite_connection = sqlite3.connect('game_data.db')
        cursor = sqlite_connection.cursor()

        sqlite_insert_query = f"""INSERT INTO results
                              (player_nick, score)
                              VALUES (?, ?);"""
        data_tuple = (NAME, RESULT)
        cursor.execute(sqlite_insert_query, data_tuple)
        sqlite_connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()


# эти комментарии никто не прочитает, я просто жду, пока этот идиот закомитит свою часть
def start_screen():
    intro_text = ["MEMory game", "",
                  "Правила игры:",
                  "После нажатия на любую клавишу вы увидите поле из кратинок",
                  "У вас есть три секунды, чтобы запомнить их положние",
                  "После чего они закроются и вам нужно будет их открыть по памяти", "",
                  "Сейчас вы увидете меню, в котором сможете выбрать сложность игры и ввести свое имя",
                  "Для того, чтобы все работало корректно, после выбора имени нажмите enter"
                  "Для выбора сложности прокликайте его!""",
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


meme_test = load_image('meme1.jpg')
meme_rect = meme_test.get_rect(
    bottomright=(WINDOWWIDTH, WINDOWHEIGHT))
Screen.blit(meme_test, meme_rect)

FIRST_OPPENED = False


# сцена победы
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("victory")
    screen.fill((0, 0, 0))
    global NAME, RESULT

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                save_bd()
                main()
        font = pygame.font.Font(None, 50)
        text = font.render("Поздравляем, вы выйграли", False, 'red')
        text2 = font.render(f"Ваш счёт: {str(RESULT)}", False, 'red')
        text3 = font.render("Нажмите на любую клавишу,", False, 'red')
        text4 = font.render("чтобы продолжить", False, 'red')
        Screen.blit(text, [200, 200])
        Screen.blit(text2, [240, 240])
        Screen.blit(text3, [180, 280])
        Screen.blit(text4, [200, 320])
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


# игровой цикл
def game(diff):
    global COORDS, FIRST_OPPENED, COUNTER, RESULT
    if diff == 0:
        Screen.fill((100, 100, 100))
        board = Board(4, 4)
        board.set_view(100, 100, 80)
        board.render()
        running = True

        # далее и ниже:
        # meme()_test() зашрузка картинки и её пары

        meme1_test1 = pygame.image.load('data/meme1.jpg')
        meme1_rect1 = meme_test.get_rect(bottomright=(180, 180))
        Screen.blit(meme1_test1, meme1_rect1)
        meme1_test2 = pygame.image.load('data/meme1.jpg')
        meme1_rect2 = meme_test.get_rect(bottomright=(340, 340))
        Screen.blit(meme1_test2, meme1_rect2)

        meme2_test1 = pygame.image.load('data/meme2.jpg')
        meme2_rect1 = meme_test.get_rect(bottomright=(260, 180))
        Screen.blit(meme2_test1, meme2_rect1)
        meme2_test2 = pygame.image.load('data/meme2.jpg')
        meme2_rect2 = meme_test.get_rect(bottomright=(260, 420))
        Screen.blit(meme2_test2, meme2_rect2)

        meme3_test1 = pygame.image.load('data/meme3.png')
        meme3_rect1 = meme_test.get_rect(bottomright=(420, 180))
        Screen.blit(meme3_test1, meme3_rect1)
        meme3_test2 = pygame.image.load('data/meme3.png')
        meme3_rect2 = meme_test.get_rect(bottomright=(260, 340))
        Screen.blit(meme3_test2, meme3_rect2)

        meme4_test1 = pygame.image.load('data/meme4.jpg')
        meme4_rect1 = meme_test.get_rect(bottomright=(260, 260))
        Screen.blit(meme4_test1, meme4_rect1)
        meme4_test2 = pygame.image.load('data/meme4.jpg')
        meme4_rect2 = meme_test.get_rect(bottomright=(420, 420))
        Screen.blit(meme4_test2, meme4_rect2)

        meme5_test1 = pygame.image.load('data/meme5.jpg')
        meme5_rect1 = meme_test.get_rect(bottomright=(340, 180))
        Screen.blit(meme5_test1, meme5_rect1)
        meme5_test2 = pygame.image.load('data/meme5.jpg')
        meme5_rect2 = meme_test.get_rect(bottomright=(180, 420))
        Screen.blit(meme5_test2, meme5_rect2)

        meme6_test1 = pygame.image.load('data/meme6.png')
        meme6_rect1 = meme_test.get_rect(bottomright=(340, 260))
        Screen.blit(meme6_test1, meme6_rect1)
        meme6_test2 = pygame.image.load('data/meme6.png')
        meme6_rect2 = meme_test.get_rect(bottomright=(340, 420))
        Screen.blit(meme6_test2, meme6_rect2)

        meme7_test1 = pygame.image.load('data/meme7.png')
        meme7_rect1 = meme_test.get_rect(bottomright=(180, 260))
        Screen.blit(meme7_test1, meme7_rect1)
        meme7_test2 = pygame.image.load('data/meme7.png')
        meme7_rect2 = meme_test.get_rect(bottomright=(420, 340))
        Screen.blit(meme7_test2, meme7_rect2)

        meme8_test1 = load_image('meme8.png')
        meme8_rect1 = meme_test.get_rect(bottomright=(180, 340))
        Screen.blit(meme8_test1, meme8_rect1)
        meme8_test2 = load_image('meme8.png')
        meme8_rect2 = meme_test.get_rect(bottomright=(420, 260))
        Screen.blit(meme8_test2, meme8_rect2)

        pygame.display.flip()
        time.sleep(1.75)

        # ниже прописаны ячейки закрывающие мэмчики

        leaf1_1 = pygame.image.load('data/okno.png')
        leaf1_rect1 = leaf1_1.get_rect(bottomright=(180, 180))
        Screen.blit(leaf1_1, leaf1_rect1)
        leaf1_2 = pygame.image.load('data/okno.png')
        leaf1_rect2 = leaf1_2.get_rect(bottomright=(340, 340))
        Screen.blit(leaf1_2, leaf1_rect2)

        leaf2_1 = pygame.image.load('data/okno.png')
        leaf2_rect1 = leaf2_1.get_rect(bottomright=(260, 180))
        Screen.blit(leaf2_1, leaf2_rect1)
        leaf2_2 = pygame.image.load('data/okno.png')
        leaf2_rect2 = leaf2_2.get_rect(bottomright=(260, 420))
        Screen.blit(leaf2_2, leaf2_rect2)

        leaf3_1 = pygame.image.load('data/okno.png')
        leaf3_rect1 = leaf3_1.get_rect(bottomright=(420, 180))
        Screen.blit(leaf3_1, leaf3_rect1)
        leaf3_2 = pygame.image.load('data/okno.png')
        leaf3_rect2 = leaf3_2.get_rect(bottomright=(260, 340))
        Screen.blit(leaf3_2, leaf3_rect2)

        leaf4_1 = pygame.image.load('data/okno.png')
        leaf4_rect1 = leaf4_1.get_rect(bottomright=(260, 260))
        Screen.blit(leaf4_1, leaf4_rect1)
        leaf4_2 = pygame.image.load('data/okno.png')
        leaf4_rect2 = leaf4_2.get_rect(bottomright=(420, 420))
        Screen.blit(leaf4_2, leaf4_rect2)

        leaf5_1 = pygame.image.load('data/okno.png')
        leaf5_rect1 = leaf5_1.get_rect(bottomright=(340, 180))
        Screen.blit(leaf5_1, leaf5_rect1)
        leaf5_2 = pygame.image.load('data/okno.png')
        leaf5_rect2 = leaf5_2.get_rect(bottomright=(180, 420))
        Screen.blit(leaf5_2, leaf5_rect2)

        leaf6_1 = pygame.image.load('data/okno.png')
        leaf6_rect1 = leaf6_1.get_rect(bottomright=(340, 260))
        Screen.blit(leaf6_1, leaf6_rect1)
        leaf6_2 = pygame.image.load('data/okno.png')
        leaf6_rect2 = leaf6_2.get_rect(bottomright=(340, 420))
        Screen.blit(leaf6_2, leaf6_rect2)

        leaf7_1 = pygame.image.load('data/okno.png')
        leaf7_rect1 = leaf7_1.get_rect(bottomright=(180, 260))
        Screen.blit(leaf7_1, leaf7_rect1)
        leaf7_2 = pygame.image.load('data/okno.png')
        leaf7_rect2 = leaf7_2.get_rect(bottomright=(420, 340))
        Screen.blit(leaf7_2, leaf7_rect2)

        leaf8_1 = pygame.image.load('data/okno.png')
        leaf8_rect1 = leaf8_1.get_rect(bottomright=(180, 340))
        Screen.blit(leaf8_1, leaf8_rect1)
        leaf8_2 = pygame.image.load('data/okno.png')
        leaf8_rect2 = leaf8_2.get_rect(bottomright=(420, 260))
        Screen.blit(leaf8_2, leaf8_rect2)

        pygame.display.flip()
        old = None
        while running:
            if COUNTER == 8:
                running = False
                run_game()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    a = board.get_click(event.pos)

                    if FIRST_OPPENED:  # вот эта ебала проверяет наличие открытой клетки

                        # далее и ниже прописана проверка правильных пар для ячеек

                        if old == (0, 0):
                            if a == (2, 2):
                                meme1_test2 = pygame.image.load('data/meme1.jpg')
                                meme1_rect2 = meme_test.get_rect(bottomright=(340, 340))
                                Screen.blit(meme1_test2, meme1_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf1_1 = pygame.image.load('data/okno.png')
                                leaf1_rect1 = leaf1_1.get_rect(bottomright=(180, 180))
                                Screen.blit(leaf1_1, leaf1_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (0, 1):
                            if a == (3, 1):
                                meme2_test2 = pygame.image.load('data/meme2.jpg')
                                meme2_rect2 = meme_test.get_rect(bottomright=(260, 420))
                                Screen.blit(meme2_test2, meme2_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf2_1 = pygame.image.load('data/okno.png')
                                leaf2_rect1 = leaf2_1.get_rect(bottomright=(260, 180))
                                Screen.blit(leaf2_1, leaf2_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (0, 2):
                            if a == (3, 0):
                                meme5_test2 = pygame.image.load('data/meme5.jpg')
                                meme5_rect2 = meme_test.get_rect(bottomright=(180, 420))
                                Screen.blit(meme5_test2, meme5_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf5_1 = pygame.image.load('data/okno.png')
                                leaf5_rect1 = leaf5_1.get_rect(bottomright=(340, 180))
                                Screen.blit(leaf5_1, leaf5_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (0, 3):
                            if a == (2, 1):
                                meme3_test2 = pygame.image.load('data/meme3.png')
                                meme3_rect2 = meme_test.get_rect(bottomright=(260, 340))
                                Screen.blit(meme3_test2, meme3_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf3_1 = pygame.image.load('data/okno.png')
                                leaf3_rect1 = leaf3_1.get_rect(bottomright=(420, 180))
                                Screen.blit(leaf3_1, leaf3_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (1, 0):
                            if a == (2, 3):
                                meme7_test2 = pygame.image.load('data/meme7.png')
                                meme7_rect2 = meme_test.get_rect(bottomright=(420, 340))
                                Screen.blit(meme7_test2, meme7_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf7_1 = pygame.image.load('data/okno.png')
                                leaf7_rect1 = leaf7_1.get_rect(bottomright=(180, 260))
                                Screen.blit(leaf7_1, leaf7_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (1, 1):
                            if a == (3, 3):
                                meme4_test2 = pygame.image.load('data/meme4.jpg')
                                meme4_rect2 = meme_test.get_rect(bottomright=(420, 420))
                                Screen.blit(meme4_test2, meme4_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf4_1 = pygame.image.load('data/okno.png')
                                leaf4_rect1 = leaf4_1.get_rect(bottomright=(260, 260))
                                Screen.blit(leaf4_1, leaf4_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (1, 2):
                            if a == (3, 2):
                                meme6_test2 = pygame.image.load('data/meme6.png')
                                meme6_rect2 = meme_test.get_rect(bottomright=(340, 420))
                                Screen.blit(meme6_test2, meme6_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf6_1 = pygame.image.load('data/okno.png')
                                leaf6_rect1 = leaf6_1.get_rect(bottomright=(340, 260))
                                Screen.blit(leaf6_1, leaf6_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (1, 3):
                            if a == (2, 0):
                                meme8_test1 = load_image('meme8.png')
                                meme8_rect1 = meme_test.get_rect(bottomright=(180, 340))
                                Screen.blit(meme8_test1, meme8_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf8_2 = load_image('okno.png')
                                leaf8_rect2 = leaf8_2.get_rect(bottomright=(420, 260))
                                Screen.blit(leaf8_2, leaf8_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (2, 0):
                            if a == (1, 3):
                                meme8_test2 = load_image('meme8.png')
                                meme8_rect2 = meme_test.get_rect(bottomright=(420, 260))
                                Screen.blit(meme8_test2, meme8_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf8_1 = load_image('okno.png')
                                leaf8_rect1 = leaf8_1.get_rect(bottomright=(180, 340))
                                Screen.blit(leaf8_1, leaf8_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        FIRST_OPPENED = False
                        if old == (2, 1):
                            if a == (0, 3):
                                meme3_test1 = pygame.image.load('data/meme3.png')
                                meme3_rect1 = meme_test.get_rect(bottomright=(420, 180))
                                Screen.blit(meme3_test1, meme3_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf3_2 = pygame.image.load('data/okno.png')
                                leaf3_rect2 = leaf3_2.get_rect(bottomright=(260, 340))
                                Screen.blit(leaf3_2, leaf3_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (2, 2):
                            if a == (0, 0):
                                meme1_test1 = load_image('meme1.jpg')
                                meme1_rect1 = meme_test.get_rect(bottomright=(180, 180))
                                Screen.blit(meme1_test1, meme1_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf1_2 = load_image('okno.png')
                                leaf1_rect2 = leaf1_2.get_rect(bottomright=(340, 340))
                                Screen.blit(leaf1_2, leaf1_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (2, 3):
                            if a == (1, 0):
                                meme7_test1 = load_image('meme7.png')
                                meme7_rect1 = meme_test.get_rect(bottomright=(180, 260))
                                Screen.blit(meme7_test1, meme7_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf7_2 = load_image('okno.png')
                                leaf7_rect2 = leaf7_2.get_rect(bottomright=(420, 340))
                                Screen.blit(leaf7_2, leaf7_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        FIRST_OPPENED = False
                        if old == (3, 0):
                            if a == (0, 2):
                                meme5_test1 = load_image('meme5.jpg')
                                meme5_rect1 = meme_test.get_rect(bottomright=(340, 180))
                                Screen.blit(meme5_test1, meme5_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf5_2 = load_image('okno.png')
                                leaf5_rect2 = leaf5_2.get_rect(bottomright=(180, 420))
                                Screen.blit(leaf5_2, leaf5_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (3, 1):
                            if a == (0, 1):
                                meme2_test1 = load_image('meme2.jpg')
                                meme2_rect1 = meme_test.get_rect(bottomright=(260, 180))
                                Screen.blit(meme2_test1, meme2_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf2_2 = load_image('okno.png')
                                leaf2_rect2 = leaf2_2.get_rect(bottomright=(260, 420))
                                Screen.blit(leaf2_2, leaf2_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (3, 2):
                            if a == (1, 2):
                                meme6_test1 = load_image('meme6.png')
                                meme6_rect1 = meme_test.get_rect(bottomright=(340, 260))
                                Screen.blit(meme6_test1, meme6_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf6_2 = load_image('okno.png')
                                leaf6_rect2 = leaf6_2.get_rect(bottomright=(340, 420))
                                Screen.blit(leaf6_2, leaf6_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        if old == (3, 3):
                            if a == (1, 1):
                                meme4_test1 = load_image('meme4.jpg')
                                meme4_rect1 = meme_test.get_rect(bottomright=(260, 260))
                                Screen.blit(meme4_test1, meme4_rect1)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                COUNTER += 1
                            else:
                                leaf4_2 = load_image('okno.png')
                                leaf4_rect2 = leaf4_2.get_rect(bottomright=(420, 420))
                                Screen.blit(leaf4_2, leaf4_rect2)
                                FIRST_OPPENED = False
                                a = None
                                old = None
                                RESULT -= 500
                        FIRST_OPPENED = False

                    if not FIRST_OPPENED:  # а вот эта ебала делает первую ячейку непосредственно открытой
                        print('entered')
                        if a == (0, 0):
                            meme1_test1 = pygame.image.load('data/meme1.jpg')
                            meme1_rect1 = meme_test.get_rect(bottomright=(180, 180))
                            Screen.blit(meme1_test1, meme1_rect1)
                        if a == (0, 1):
                            meme2_test1 = pygame.image.load('data/meme2.jpg')
                            meme2_rect1 = meme_test.get_rect(bottomright=(260, 180))
                            Screen.blit(meme2_test1, meme2_rect1)
                        if a == (0, 2):
                            meme5_test1 = pygame.image.load('data/meme5.jpg')
                            meme5_rect1 = meme_test.get_rect(bottomright=(340, 180))
                            Screen.blit(meme5_test1, meme5_rect1)
                        if a == (0, 3):
                            meme3_test1 = pygame.image.load('data/meme3.png')
                            meme3_rect1 = meme_test.get_rect(bottomright=(420, 180))
                            Screen.blit(meme3_test1, meme3_rect1)
                        if a == (1, 0):
                            meme7_test1 = pygame.image.load('data/meme7.png')
                            meme7_rect1 = meme_test.get_rect(bottomright=(180, 260))
                            Screen.blit(meme7_test1, meme7_rect1)
                        if a == (1, 1):
                            meme4_test1 = pygame.image.load('data/meme4.jpg')
                            meme4_rect1 = meme_test.get_rect(bottomright=(260, 260))
                            Screen.blit(meme4_test1, meme4_rect1)
                        if a == (1, 2):
                            meme6_test1 = pygame.image.load('data/meme6.png')
                            meme6_rect1 = meme_test.get_rect(bottomright=(340, 260))
                            Screen.blit(meme6_test1, meme6_rect1)
                        if a == (1, 3):
                            meme8_test2 = load_image('meme8.png')
                            meme8_rect2 = meme_test.get_rect(bottomright=(420, 260))
                            Screen.blit(meme8_test2, meme8_rect2)
                        if a == (2, 0):
                            meme8_test1 = load_image('meme8.png')
                            meme8_rect1 = meme_test.get_rect(bottomright=(180, 340))
                            Screen.blit(meme8_test1, meme8_rect1)
                        if a == (2, 1):
                            meme3_test2 = pygame.image.load('data/meme3.png')
                            meme3_rect2 = meme_test.get_rect(bottomright=(260, 340))
                            Screen.blit(meme3_test2, meme3_rect2)
                        if a == (2, 2):
                            meme1_test2 = pygame.image.load('data/meme1.jpg')
                            meme1_rect2 = meme_test.get_rect(bottomright=(340, 340))
                            Screen.blit(meme1_test2, meme1_rect2)
                        if a == (2, 3):
                            meme7_test2 = pygame.image.load('data/meme7.png')
                            meme7_rect2 = meme_test.get_rect(bottomright=(420, 340))
                            Screen.blit(meme7_test2, meme7_rect2)
                        if a == (3, 0):
                            meme5_test2 = pygame.image.load('data/meme5.jpg')
                            meme5_rect2 = meme_test.get_rect(bottomright=(180, 420))
                            Screen.blit(meme5_test2, meme5_rect2)
                        if a == (3, 1):
                            meme2_test2 = pygame.image.load('data/meme2.jpg')
                            meme2_rect2 = meme_test.get_rect(bottomright=(260, 420))
                            Screen.blit(meme2_test2, meme2_rect2)
                        if a == (3, 2):
                            meme6_test2 = pygame.image.load('data/meme6.png')
                            meme6_rect2 = meme_test.get_rect(bottomright=(340, 420))
                            Screen.blit(meme6_test2, meme6_rect2)
                        if a == (3, 3):
                            meme4_test2 = pygame.image.load('data/meme4.jpg')
                            meme4_rect2 = meme_test.get_rect(bottomright=(420, 420))
                            Screen.blit(meme4_test2, meme4_rect2)
                        FIRST_OPPENED = True
                        old = a

            # прописывает очки

            font = pygame.font.Font(None, 50)
            Screen.fill(pygame.Color('grey'), pygame.Rect(0, 0, 300, 80))
            text = font.render("Очки: ", False, 'red')
            text2 = font.render(str(RESULT), False, 'red')
            Screen.blit(text, [20, 20])
            Screen.blit(text2, [150, 20])
            pygame.display.flip()

        pygame.quit()

    if diff == 1:
        global HARD_COUNTER
        Screen.fill((100, 100, 100))
        board = Board(6, 6)
        board.set_view(100, 100, 80)
        board.render()
        running = True
        meme1_test1 = pygame.image.load('data/meme1.jpg')
        meme1_rect1 = meme_test.get_rect(bottomright=(180, 180))
        Screen.blit(meme1_test1, meme1_rect1)
        meme1_test2 = pygame.image.load('data/meme1.jpg')
        meme1_rect2 = meme_test.get_rect(bottomright=(340, 340))
        Screen.blit(meme1_test2, meme1_rect2)

        meme2_test1 = pygame.image.load('data/meme2.jpg')
        meme2_rect1 = meme_test.get_rect(bottomright=(260, 180))
        Screen.blit(meme2_test1, meme2_rect1)
        meme2_test2 = pygame.image.load('data/meme2.jpg')
        meme2_rect2 = meme_test.get_rect(bottomright=(260, 420))
        Screen.blit(meme2_test2, meme2_rect2)

        meme3_test1 = pygame.image.load('data/meme3.png')
        meme3_rect1 = meme_test.get_rect(bottomright=(420, 180))
        Screen.blit(meme3_test1, meme3_rect1)
        meme3_test2 = pygame.image.load('data/meme3.png')
        meme3_rect2 = meme_test.get_rect(bottomright=(260, 340))
        Screen.blit(meme3_test2, meme3_rect2)

        meme4_test1 = pygame.image.load('data/meme4.jpg')
        meme4_rect1 = meme_test.get_rect(bottomright=(260, 260))
        Screen.blit(meme4_test1, meme4_rect1)
        meme4_test2 = pygame.image.load('data/meme4.jpg')
        meme4_rect2 = meme_test.get_rect(bottomright=(420, 420))
        Screen.blit(meme4_test2, meme4_rect2)

        meme5_test1 = pygame.image.load('data/meme5.jpg')
        meme5_rect1 = meme_test.get_rect(bottomright=(340, 180))
        Screen.blit(meme5_test1, meme5_rect1)
        meme5_test2 = pygame.image.load('data/meme5.jpg')
        meme5_rect2 = meme_test.get_rect(bottomright=(180, 420))
        Screen.blit(meme5_test2, meme5_rect2)

        meme6_test1 = pygame.image.load('data/meme6.png')
        meme6_rect1 = meme_test.get_rect(bottomright=(340, 260))
        Screen.blit(meme6_test1, meme6_rect1)
        meme6_test2 = pygame.image.load('data/meme6.png')
        meme6_rect2 = meme_test.get_rect(bottomright=(340, 420))
        Screen.blit(meme6_test2, meme6_rect2)

        meme7_test1 = pygame.image.load('data/meme7.png')
        meme7_rect1 = meme_test.get_rect(bottomright=(180, 260))
        Screen.blit(meme7_test1, meme7_rect1)
        meme7_test2 = pygame.image.load('data/meme7.png')
        meme7_rect2 = meme_test.get_rect(bottomright=(420, 340))
        Screen.blit(meme7_test2, meme7_rect2)

        meme8_test1 = load_image('meme8.png')
        meme8_rect1 = meme_test.get_rect(bottomright=(180, 340))
        Screen.blit(meme8_test1, meme8_rect1)
        meme8_test2 = load_image('meme8.png')
        meme8_rect2 = meme_test.get_rect(bottomright=(420, 260))
        Screen.blit(meme8_test2, meme8_rect2)

        meme9_test1 = load_image('meme9.png')
        meme9_rect1 = meme_test.get_rect(bottomright=(180, 500))
        Screen.blit(meme9_test1, meme9_rect1)
        meme9_test2 = load_image('meme9.png')
        meme9_rect2 = meme_test.get_rect(bottomright=(500, 260))
        Screen.blit(meme9_test2, meme9_rect2)

        meme9jpg_test1 = load_image('meme9.jpg')
        meme9jpg_rect1 = meme_test.get_rect(bottomright=(340, 500))
        Screen.blit(meme9jpg_test1, meme9jpg_rect1)
        meme9jpg_test2 = load_image('meme9.jpg')
        meme9jpg_rect2 = meme_test.get_rect(bottomright=(580, 500))
        Screen.blit(meme9jpg_test2, meme9jpg_rect2)

        meme10_test1 = load_image('meme10.png')
        meme10_rect1 = meme_test.get_rect(bottomright=(580, 180))
        Screen.blit(meme10_test1, meme10_rect1)
        meme10_test2 = load_image('meme10.png')
        meme10_rect2 = meme_test.get_rect(bottomright=(500, 500))
        Screen.blit(meme10_test2, meme10_rect2)

        meme11_test1 = load_image('meme11.jpg')
        meme11_rect1 = meme_test.get_rect(bottomright=(500, 180))
        Screen.blit(meme11_test1, meme11_rect1)
        meme11_test2 = load_image('meme11.jpg')
        meme11_rect2 = meme_test.get_rect(bottomright=(420, 500))
        Screen.blit(meme11_test2, meme11_rect2)

        meme12_test1 = load_image('meme12.jpg')
        meme12_rect1 = meme_test.get_rect(bottomright=(580, 260))
        Screen.blit(meme12_test1, meme12_rect1)
        meme12_test2 = load_image('meme12.jpg')
        meme12_rect2 = meme_test.get_rect(bottomright=(340, 580))
        Screen.blit(meme12_test2, meme12_rect2)

        meme13_test1 = load_image('meme13.jpg')
        meme13_rect1 = meme_test.get_rect(bottomright=(580, 580))
        Screen.blit(meme13_test1, meme13_rect1)
        meme13_test2 = load_image('meme13.jpg')
        meme13_rect2 = meme_test.get_rect(bottomright=(260, 500))
        Screen.blit(meme13_test2, meme13_rect2)

        meme14_test1 = load_image('meme14.png')
        meme14_rect1 = meme_test.get_rect(bottomright=(180, 580))
        Screen.blit(meme14_test1, meme14_rect1)
        meme14_test2 = load_image('meme14.png')
        meme14_rect2 = meme_test.get_rect(bottomright=(500, 340))
        Screen.blit(meme14_test2, meme14_rect2)

        meme15_test1 = load_image('meme15.jpg')
        meme15_rect1 = meme_test.get_rect(bottomright=(260, 580))
        Screen.blit(meme15_test1, meme15_rect1)
        meme15_test2 = load_image('meme15.jpg')
        meme15_rect2 = meme_test.get_rect(bottomright=(500, 420))
        Screen.blit(meme15_test2, meme15_rect2)

        meme16_test1 = load_image('meme16.jpg')
        meme16_rect1 = meme_test.get_rect(bottomright=(420, 580))
        Screen.blit(meme16_test1, meme16_rect1)
        meme16_test2 = load_image('meme16.jpg')
        meme16_rect2 = meme_test.get_rect(bottomright=(580, 420))
        Screen.blit(meme16_test2, meme16_rect2)

        meme17_test1 = load_image('meme17.jpg')
        meme17_rect1 = meme_test.get_rect(bottomright=(500, 580))
        Screen.blit(meme17_test1, meme17_rect1)
        meme17_test2 = load_image('meme17.jpg')
        meme17_rect2 = meme_test.get_rect(bottomright=(580, 340))
        Screen.blit(meme17_test2, meme17_rect2)
        pygame.display.flip()
        time.sleep(2)

        leaf1_1 = pygame.image.load('data/okno.png')
        leaf1_rect1 = leaf1_1.get_rect(bottomright=(180, 180))
        Screen.blit(leaf1_1, leaf1_rect1)

        leaf1_2 = pygame.image.load('data/okno.png')
        leaf1_rect2 = leaf1_2.get_rect(bottomright=(340, 340))
        Screen.blit(leaf1_2, leaf1_rect2)

        leaf2_1 = pygame.image.load('data/okno.png')
        leaf2_rect1 = leaf2_1.get_rect(bottomright=(260, 180))
        Screen.blit(leaf2_1, leaf2_rect1)

        leaf2_2 = pygame.image.load('data/okno.png')
        leaf2_rect2 = leaf2_2.get_rect(bottomright=(260, 420))
        Screen.blit(leaf2_2, leaf2_rect2)

        leaf3_1 = pygame.image.load('data/okno.png')
        leaf3_rect1 = leaf3_1.get_rect(bottomright=(420, 180))
        Screen.blit(leaf3_1, leaf3_rect1)

        leaf3_2 = pygame.image.load('data/okno.png')
        leaf3_rect2 = leaf3_2.get_rect(bottomright=(260, 340))
        Screen.blit(leaf3_2, leaf3_rect2)

        leaf4_1 = pygame.image.load('data/okno.png')
        leaf4_rect1 = leaf4_1.get_rect(bottomright=(260, 260))
        Screen.blit(leaf4_1, leaf4_rect1)

        leaf4_2 = pygame.image.load('data/okno.png')
        leaf4_rect2 = leaf4_2.get_rect(bottomright=(420, 420))
        Screen.blit(leaf4_2, leaf4_rect2)

        leaf5_1 = pygame.image.load('data/okno.png')
        leaf5_rect1 = leaf5_1.get_rect(bottomright=(340, 180))
        Screen.blit(leaf5_1, leaf5_rect1)

        leaf5_2 = pygame.image.load('data/okno.png')
        leaf5_rect2 = leaf5_2.get_rect(bottomright=(180, 420))
        Screen.blit(leaf5_2, leaf5_rect2)

        leaf6_1 = pygame.image.load('data/okno.png')
        leaf6_rect1 = leaf6_1.get_rect(bottomright=(340, 260))
        Screen.blit(leaf6_1, leaf6_rect1)

        leaf6_2 = pygame.image.load('data/okno.png')
        leaf6_rect2 = leaf6_2.get_rect(bottomright=(340, 420))
        Screen.blit(leaf6_2, leaf6_rect2)

        leaf7_1 = pygame.image.load('data/okno.png')
        leaf7_rect1 = leaf7_1.get_rect(bottomright=(180, 260))
        Screen.blit(leaf7_1, leaf7_rect1)

        leaf7_2 = pygame.image.load('data/okno.png')
        leaf7_rect2 = leaf7_2.get_rect(bottomright=(420, 340))
        Screen.blit(leaf7_2, leaf7_rect2)

        leaf8_1 = pygame.image.load('data/okno.png')
        leaf8_rect1 = leaf8_1.get_rect(bottomright=(180, 340))
        Screen.blit(leaf8_1, leaf8_rect1)

        leaf8_2 = pygame.image.load('data/okno.png')
        leaf8_rect2 = leaf8_2.get_rect(bottomright=(420, 260))
        Screen.blit(leaf8_2, leaf8_rect2)

        leaf9_1 = pygame.image.load('data/okno.png')
        leaf9_rect1 = leaf9_1.get_rect(bottomright=(180, 500))
        Screen.blit(leaf9_1, leaf9_rect1)

        leaf9_2 = pygame.image.load('data/okno.png')
        leaf9_rect2 = leaf9_2.get_rect(bottomright=(500, 260))
        Screen.blit(leaf9_2, leaf9_rect2)

        leaf9jpg_1 = pygame.image.load('data/okno.png')
        leaf9jpg_rect1 = leaf9jpg_1.get_rect(bottomright=(340, 500))
        Screen.blit(leaf9jpg_1, leaf9jpg_rect1)

        leaf9jpg_2 = pygame.image.load('data/okno.png')
        leaf9jpg_rect2 = leaf9jpg_2.get_rect(bottomright=(580, 500))
        Screen.blit(leaf9jpg_2, leaf9jpg_rect2)

        leaf10_1 = pygame.image.load('data/okno.png')
        leaf10_rect1 = leaf10_1.get_rect(bottomright=(580, 180))
        Screen.blit(leaf10_1, leaf10_rect1)

        leaf10_2 = pygame.image.load('data/okno.png')
        leaf10_rect2 = leaf10_2.get_rect(bottomright=(500, 500))
        Screen.blit(leaf10_2, leaf10_rect2)

        leaf11_1 = pygame.image.load('data/okno.png')
        leaf11_rect1 = leaf11_1.get_rect(bottomright=(500, 180))
        Screen.blit(leaf11_1, leaf11_rect1)

        leaf11_2 = pygame.image.load('data/okno.png')
        leaf11_rect2 = leaf11_2.get_rect(bottomright=(420, 500))
        Screen.blit(leaf11_2, leaf11_rect2)

        leaf12_1 = pygame.image.load('data/okno.png')
        leaf12_rect1 = leaf12_1.get_rect(bottomright=(580, 260))
        Screen.blit(leaf12_1, leaf12_rect1)

        leaf12_2 = pygame.image.load('data/okno.png')
        leaf12_rect2 = leaf12_2.get_rect(bottomright=(340, 580))
        Screen.blit(leaf12_2, leaf12_rect2)

        leaf13_1 = pygame.image.load('data/okno.png')
        leaf13_rect1 = leaf13_1.get_rect(bottomright=(580, 580))
        Screen.blit(leaf13_1, leaf13_rect1)

        leaf13_2 = pygame.image.load('data/okno.png')
        leaf13_rect2 = leaf13_2.get_rect(bottomright=(260, 500))
        Screen.blit(leaf13_2, leaf13_rect2)

        leaf14_1 = pygame.image.load('data/okno.png')
        leaf14_rect1 = leaf14_1.get_rect(bottomright=(180, 580))
        Screen.blit(leaf14_1, leaf14_rect1)

        leaf14_2 = pygame.image.load('data/okno.png')
        leaf14_rect2 = leaf14_2.get_rect(bottomright=(500, 340))
        Screen.blit(leaf14_2, leaf14_rect2)

        leaf15_1 = pygame.image.load('data/okno.png')
        leaf15_rect1 = leaf15_1.get_rect(bottomright=(260, 580))
        Screen.blit(leaf15_1, leaf15_rect1)

        leaf15_2 = pygame.image.load('data/okno.png')
        leaf15_rect2 = leaf15_2.get_rect(bottomright=(500, 420))
        Screen.blit(leaf15_2, leaf15_rect2)

        leaf16_1 = pygame.image.load('data/okno.png')
        leaf16_rect1 = leaf16_1.get_rect(bottomright=(420, 580))
        Screen.blit(leaf16_1, leaf16_rect1)

        leaf16_2 = pygame.image.load('data/okno.png')
        leaf16_rect2 = leaf16_2.get_rect(bottomright=(580, 420))
        Screen.blit(leaf16_2, leaf16_rect2)

        leaf17_1 = pygame.image.load('data/okno.png')
        leaf17_rect1 = leaf17_1.get_rect(bottomright=(500, 580))
        Screen.blit(leaf17_1, leaf17_rect1)

        leaf17_2 = pygame.image.load('data/okno.png')
        leaf17_rect2 = leaf17_2.get_rect(bottomright=(580, 340))
        Screen.blit(leaf17_2, leaf17_rect2)

        pygame.display.flip()
        while running:
            if HARD_COUNTER == 16:
                running = False
                run_game()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        a = board.get_click(event.pos)

                        if FIRST_OPPENED:
                            if old == (0, 0):
                                if a == (2, 2):
                                    meme1_test2 = pygame.image.load('data/meme1.jpg')
                                    meme1_rect2 = meme_test.get_rect(bottomright=(340, 340))
                                    Screen.blit(meme1_test2, meme1_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf1_1 = pygame.image.load('data/okno.png')
                                    leaf1_rect1 = leaf1_1.get_rect(bottomright=(180, 180))
                                    Screen.blit(leaf1_1, leaf1_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (0, 1):
                                if a == (3, 1):
                                    meme2_test2 = pygame.image.load('data/meme2.jpg')
                                    meme2_rect2 = meme_test.get_rect(bottomright=(260, 420))
                                    Screen.blit(meme2_test2, meme2_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf2_1 = pygame.image.load('data/okno.png')
                                    leaf2_rect1 = leaf2_1.get_rect(bottomright=(260, 180))
                                    Screen.blit(leaf2_1, leaf2_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (0, 2):
                                if a == (3, 0):
                                    meme5_test2 = pygame.image.load('data/meme5.jpg')
                                    meme5_rect2 = meme_test.get_rect(bottomright=(180, 420))
                                    Screen.blit(meme5_test2, meme5_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf5_1 = pygame.image.load('data/okno.png')
                                    leaf5_rect1 = leaf5_1.get_rect(bottomright=(340, 180))
                                    Screen.blit(leaf5_1, leaf5_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (0, 3):
                                if a == (2, 1):
                                    meme3_test2 = pygame.image.load('data/meme3.png')
                                    meme3_rect2 = meme_test.get_rect(bottomright=(260, 340))
                                    Screen.blit(meme3_test2, meme3_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf3_1 = pygame.image.load('data/okno.png')
                                    leaf3_rect1 = leaf3_1.get_rect(bottomright=(420, 180))
                                    Screen.blit(leaf3_1, leaf3_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (1, 0):
                                if a == (2, 3):
                                    meme7_test2 = pygame.image.load('data/meme7.png')
                                    meme7_rect2 = meme_test.get_rect(bottomright=(420, 340))
                                    Screen.blit(meme7_test2, meme7_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf7_1 = pygame.image.load('data/okno.png')
                                    leaf7_rect1 = leaf7_1.get_rect(bottomright=(180, 260))
                                    Screen.blit(leaf7_1, leaf7_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (1, 1):
                                if a == (3, 3):
                                    meme4_test2 = pygame.image.load('data/meme4.jpg')
                                    meme4_rect2 = meme_test.get_rect(bottomright=(420, 420))
                                    Screen.blit(meme4_test2, meme4_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf4_1 = pygame.image.load('data/okno.png')
                                    leaf4_rect1 = leaf4_1.get_rect(bottomright=(260, 260))
                                    Screen.blit(leaf4_1, leaf4_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (1, 2):
                                if a == (3, 2):
                                    meme6_test2 = pygame.image.load('data/meme6.png')
                                    meme6_rect2 = meme_test.get_rect(bottomright=(340, 420))
                                    Screen.blit(meme6_test2, meme6_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf6_1 = pygame.image.load('data/okno.png')
                                    leaf6_rect1 = leaf6_1.get_rect(bottomright=(340, 260))
                                    Screen.blit(leaf6_1, leaf6_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (1, 3):
                                if a == (2, 0):
                                    meme8_test1 = load_image('meme8.png')
                                    meme8_rect1 = meme_test.get_rect(bottomright=(180, 340))
                                    Screen.blit(meme8_test1, meme8_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf8_2 = load_image('okno.png')
                                    leaf8_rect2 = leaf8_2.get_rect(bottomright=(420, 260))
                                    Screen.blit(leaf8_2, leaf8_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (2, 0):
                                if a == (1, 3):
                                    meme8_test2 = load_image('meme8.png')
                                    meme8_rect2 = meme_test.get_rect(bottomright=(420, 260))
                                    Screen.blit(meme8_test2, meme8_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf8_1 = load_image('okno.png')
                                    leaf8_rect1 = leaf8_1.get_rect(bottomright=(180, 340))
                                    Screen.blit(leaf8_1, leaf8_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            FIRST_OPPENED = False
                            if old == (2, 1):
                                if a == (0, 3):
                                    meme3_test1 = pygame.image.load('data/meme3.png')
                                    meme3_rect1 = meme_test.get_rect(bottomright=(420, 180))
                                    Screen.blit(meme3_test1, meme3_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf3_2 = pygame.image.load('data/okno.png')
                                    leaf3_rect2 = leaf3_2.get_rect(bottomright=(260, 340))
                                    Screen.blit(leaf3_2, leaf3_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (2, 2):
                                if a == (0, 0):
                                    meme1_test1 = load_image('meme1.jpg')
                                    meme1_rect1 = meme_test.get_rect(bottomright=(180, 180))
                                    Screen.blit(meme1_test1, meme1_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf1_2 = load_image('okno.png')
                                    leaf1_rect2 = leaf1_2.get_rect(bottomright=(340, 340))
                                    Screen.blit(leaf1_2, leaf1_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (2, 3):
                                if a == (1, 0):
                                    meme7_test1 = load_image('meme7.png')
                                    meme7_rect1 = meme_test.get_rect(bottomright=(180, 260))
                                    Screen.blit(meme7_test1, meme7_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf7_2 = load_image('okno.png')
                                    leaf7_rect2 = leaf7_2.get_rect(bottomright=(420, 340))
                                    Screen.blit(leaf7_2, leaf7_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            FIRST_OPPENED = False
                            if old == (3, 0):
                                if a == (0, 2):
                                    meme5_test1 = load_image('meme5.jpg')
                                    meme5_rect1 = meme_test.get_rect(bottomright=(340, 180))
                                    Screen.blit(meme5_test1, meme5_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf5_2 = load_image('okno.png')
                                    leaf5_rect2 = leaf5_2.get_rect(bottomright=(180, 420))
                                    Screen.blit(leaf5_2, leaf5_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (3, 1):
                                if a == (0, 1):
                                    meme2_test1 = load_image('meme2.jpg')
                                    meme2_rect1 = meme_test.get_rect(bottomright=(260, 180))
                                    Screen.blit(meme2_test1, meme2_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf2_2 = load_image('okno.png')
                                    leaf2_rect2 = leaf2_2.get_rect(bottomright=(260, 420))
                                    Screen.blit(leaf2_2, leaf2_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (3, 2):
                                if a == (1, 2):
                                    meme6_test1 = load_image('meme6.png')
                                    meme6_rect1 = meme_test.get_rect(bottomright=(340, 260))
                                    Screen.blit(meme6_test1, meme6_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf6_2 = load_image('okno.png')
                                    leaf6_rect2 = leaf6_2.get_rect(bottomright=(340, 420))
                                    Screen.blit(leaf6_2, leaf6_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (3, 3):
                                if a == (1, 1):
                                    meme4_test1 = load_image('meme4.jpg')
                                    meme4_rect1 = meme_test.get_rect(bottomright=(260, 260))
                                    Screen.blit(meme4_test1, meme4_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf4_2 = load_image('okno.png')
                                    leaf4_rect2 = leaf4_2.get_rect(bottomright=(420, 420))
                                    Screen.blit(leaf4_2, leaf4_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (0, 4):
                                if a == (4, 3):
                                    meme11_test2 = load_image('meme11.jpg')
                                    meme11_rect2 = meme_test.get_rect(bottomright=(420, 500))
                                    Screen.blit(meme11_test2, meme11_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf11_1 = pygame.image.load('data/okno.png')
                                    leaf11_rect1 = leaf11_1.get_rect(bottomright=(500, 180))
                                    Screen.blit(leaf11_1, leaf11_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (0, 5):
                                if a == (4, 4):
                                    meme10_test2 = load_image('meme10.png')
                                    meme10_rect2 = meme_test.get_rect(bottomright=(500, 500))
                                    Screen.blit(meme10_test2, meme10_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf10_1 = pygame.image.load('data/okno.png')
                                    leaf10_rect1 = leaf10_1.get_rect(bottomright=(580, 180))
                                    Screen.blit(leaf10_1, leaf10_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (1, 4):
                                if a == (4, 0):
                                    meme9_test1 = load_image('meme9.png')
                                    meme9_rect1 = meme_test.get_rect(bottomright=(180, 500))
                                    Screen.blit(meme9_test1, meme9_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf9_2 = pygame.image.load('data/okno.png')
                                    leaf9_rect2 = leaf9_2.get_rect(bottomright=(500, 260))
                                    Screen.blit(leaf9_2, leaf9_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (1, 5):
                                if a == (5, 2):
                                    meme12_test2 = load_image('meme12.jpg')
                                    meme12_rect2 = meme_test.get_rect(bottomright=(340, 580))
                                    Screen.blit(meme12_test2, meme12_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf12_1 = pygame.image.load('data/okno.png')
                                    leaf12_rect1 = leaf12_1.get_rect(bottomright=(580, 260))
                                    Screen.blit(leaf12_1, leaf12_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (2, 4):
                                if a == (5, 0):
                                    meme14_test1 = load_image('meme14.png')
                                    meme14_rect1 = meme_test.get_rect(bottomright=(180, 580))
                                    Screen.blit(meme14_test1, meme14_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf14_2 = pygame.image.load('data/okno.png')
                                    leaf14_rect2 = leaf14_2.get_rect(bottomright=(500, 340))
                                    Screen.blit(leaf14_2, leaf14_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (2, 5):
                                if a == (5, 4):
                                    meme17_test1 = load_image('meme17.jpg')
                                    meme17_rect1 = meme_test.get_rect(bottomright=(500, 580))
                                    Screen.blit(meme17_test1, meme17_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf17_2 = pygame.image.load('data/okno.png')
                                    leaf17_rect2 = leaf17_2.get_rect(bottomright=(580, 340))
                                    Screen.blit(leaf17_2, leaf17_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (3, 4):
                                if a == (5, 1):
                                    meme15_test1 = load_image('meme15.jpg')
                                    meme15_rect1 = meme_test.get_rect(bottomright=(260, 580))
                                    Screen.blit(meme15_test1, meme15_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf15_2 = pygame.image.load('data/okno.png')
                                    leaf15_rect2 = leaf15_2.get_rect(bottomright=(500, 420))
                                    Screen.blit(leaf15_2, leaf15_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (3, 5):
                                if a == (5, 3):
                                    meme16_test1 = load_image('meme16.jpg')
                                    meme16_rect1 = meme_test.get_rect(bottomright=(420, 580))
                                    Screen.blit(meme16_test1, meme16_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf16_2 = pygame.image.load('data/okno.png')
                                    leaf16_rect2 = leaf16_2.get_rect(bottomright=(580, 420))
                                    Screen.blit(leaf16_2, leaf16_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (4, 5):
                                if a == (4, 2):
                                    meme9jpg_test1 = load_image('meme9.jpg')
                                    meme9jpg_rect1 = meme_test.get_rect(bottomright=(340, 500))
                                    Screen.blit(meme9jpg_test1, meme9jpg_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf9jpg_2 = pygame.image.load('data/okno.png')
                                    leaf9jpg_rect2 = leaf9jpg_2.get_rect(bottomright=(580, 500))
                                    Screen.blit(leaf9jpg_2, leaf9jpg_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (4, 4):
                                if a == (0, 5):
                                    meme10_test1 = load_image('meme10.png')
                                    meme10_rect1 = meme_test.get_rect(bottomright=(580, 180))
                                    Screen.blit(meme10_test1, meme10_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf10_2 = pygame.image.load('data/okno.png')
                                    leaf10_rect2 = leaf10_2.get_rect(bottomright=(500, 500))
                                    Screen.blit(leaf10_2, leaf10_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (3, 4):
                                if a == (5, 1):
                                    meme15_test2 = load_image('meme15.jpg')
                                    meme15_rect2 = meme_test.get_rect(bottomright=(500, 420))
                                    Screen.blit(meme15_test2, meme15_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf15_1 = pygame.image.load('data/okno.png')
                                    leaf15_rect1 = leaf15_1.get_rect(bottomright=(260, 580))
                                    Screen.blit(leaf15_1, leaf15_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (5, 4):
                                if a == (2, 5):
                                    meme17_test2 = load_image('meme17.jpg')
                                    meme17_rect2 = meme_test.get_rect(bottomright=(580, 340))
                                    Screen.blit(meme17_test2, meme17_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf17_1 = pygame.image.load('data/okno.png')
                                    leaf17_rect1 = leaf17_1.get_rect(bottomright=(500, 580))
                                    Screen.blit(leaf17_1, leaf17_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (5, 5):
                                if a == (4, 1):
                                    meme13_test2 = load_image('meme13.jpg')
                                    meme13_rect2 = meme_test.get_rect(bottomright=(260, 500))
                                    Screen.blit(meme13_test2, meme13_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf13_1 = pygame.image.load('data/okno.png')
                                    leaf13_rect1 = leaf13_1.get_rect(bottomright=(580, 580))
                                    Screen.blit(leaf13_1, leaf13_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (5, 3):
                                if a == (3, 5):
                                    meme16_test2 = load_image('meme16.jpg')
                                    meme16_rect2 = meme_test.get_rect(bottomright=(580, 420))
                                    Screen.blit(meme16_test2, meme16_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf16_1 = pygame.image.load('data/okno.png')
                                    leaf16_rect1 = leaf16_1.get_rect(bottomright=(420, 580))
                                    Screen.blit(leaf16_1, leaf16_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (4, 3):
                                if a == (0, 4):
                                    meme11_test1 = load_image('meme11.jpg')
                                    meme11_rect1 = meme_test.get_rect(bottomright=(500, 180))
                                    Screen.blit(meme11_test1, meme11_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:

                                    leaf11_2 = pygame.image.load('data/okno.png')
                                    leaf11_rect2 = leaf11_2.get_rect(bottomright=(420, 500))
                                    Screen.blit(leaf11_2, leaf11_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (4, 2):
                                if a == (4, 5):
                                    meme9jpg_test2 = load_image('meme9.jpg')
                                    meme9jpg_rect2 = meme_test.get_rect(bottomright=(580, 500))
                                    Screen.blit(meme9jpg_test2, meme9jpg_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf9jpg_1 = pygame.image.load('data/okno.png')
                                    leaf9jpg_rect1 = leaf9jpg_1.get_rect(bottomright=(340, 500))
                                    Screen.blit(leaf9jpg_1, leaf9jpg_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (5, 2):
                                if a == (1, 5):
                                    meme12_test1 = load_image('meme12.jpg')
                                    meme12_rect1 = meme_test.get_rect(bottomright=(580, 260))
                                    Screen.blit(meme12_test1, meme12_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf12_2 = pygame.image.load('data/okno.png')
                                    leaf12_rect2 = leaf12_2.get_rect(bottomright=(340, 580))
                                    Screen.blit(leaf12_2, leaf12_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (4, 1):
                                if a == (5, 5):
                                    meme13_test1 = load_image('meme13.jpg')
                                    meme13_rect1 = meme_test.get_rect(bottomright=(580, 580))
                                    Screen.blit(meme13_test1, meme13_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf13_2 = pygame.image.load('data/okno.png')
                                    leaf13_rect2 = leaf13_2.get_rect(bottomright=(260, 500))
                                    Screen.blit(leaf13_2, leaf13_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (5, 1):
                                if a == (3, 4):
                                    meme15_test2 = load_image('meme15.jpg')
                                    meme15_rect2 = meme_test.get_rect(bottomright=(500, 420))
                                    Screen.blit(meme15_test2, meme15_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf15_1 = pygame.image.load('data/okno.png')
                                    leaf15_rect1 = leaf15_1.get_rect(bottomright=(260, 580))
                                    Screen.blit(leaf15_1, leaf15_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (4, 0):
                                if a == (1, 4):
                                    meme9_test2 = load_image('meme9.png')
                                    meme9_rect2 = meme_test.get_rect(bottomright=(500, 260))
                                    Screen.blit(meme9_test2, meme9_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf9_1 = pygame.image.load('data/okno.png')
                                    leaf9_rect1 = leaf9_1.get_rect(bottomright=(180, 500))
                                    Screen.blit(leaf9_1, leaf9_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500
                            if old == (5, 0):
                                if a == (2, 4):
                                    meme14_test2 = load_image('meme14.png')
                                    meme14_rect2 = meme_test.get_rect(bottomright=(500, 340))
                                    Screen.blit(meme14_test2, meme14_rect2)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    HARD_COUNTER += 1
                                else:
                                    leaf14_1 = pygame.image.load('data/okno.png')
                                    leaf14_rect1 = leaf14_1.get_rect(bottomright=(180, 580))
                                    Screen.blit(leaf14_1, leaf14_rect1)
                                    FIRST_OPPENED = False
                                    a = None
                                    old = None
                                    RESULT -= 500

                                    FIRST_OPPENED = False

                        if not FIRST_OPPENED:
                            print('entered')
                            if a == (0, 0):
                                meme1_test1 = pygame.image.load('data/meme1.jpg')
                                meme1_rect1 = meme_test.get_rect(bottomright=(180, 180))
                                Screen.blit(meme1_test1, meme1_rect1)
                            if a == (0, 1):
                                meme2_test1 = pygame.image.load('data/meme2.jpg')
                                meme2_rect1 = meme_test.get_rect(bottomright=(260, 180))
                                Screen.blit(meme2_test1, meme2_rect1)
                            if a == (0, 2):
                                meme5_test1 = pygame.image.load('data/meme5.jpg')
                                meme5_rect1 = meme_test.get_rect(bottomright=(340, 180))
                                Screen.blit(meme5_test1, meme5_rect1)
                            if a == (0, 3):
                                meme3_test1 = pygame.image.load('data/meme3.png')
                                meme3_rect1 = meme_test.get_rect(bottomright=(420, 180))
                                Screen.blit(meme3_test1, meme3_rect1)
                            if a == (1, 0):
                                meme7_test1 = pygame.image.load('data/meme7.png')
                                meme7_rect1 = meme_test.get_rect(bottomright=(180, 260))
                                Screen.blit(meme7_test1, meme7_rect1)
                            if a == (1, 1):
                                meme4_test1 = pygame.image.load('data/meme4.jpg')
                                meme4_rect1 = meme_test.get_rect(bottomright=(260, 260))
                                Screen.blit(meme4_test1, meme4_rect1)
                            if a == (1, 2):
                                meme6_test1 = pygame.image.load('data/meme6.png')
                                meme6_rect1 = meme_test.get_rect(bottomright=(340, 260))
                                Screen.blit(meme6_test1, meme6_rect1)
                            if a == (1, 3):
                                meme8_test2 = load_image('meme8.png')
                                meme8_rect2 = meme_test.get_rect(bottomright=(420, 260))
                                Screen.blit(meme8_test2, meme8_rect2)
                            if a == (2, 0):
                                meme8_test1 = load_image('meme8.png')
                                meme8_rect1 = meme_test.get_rect(bottomright=(180, 340))
                                Screen.blit(meme8_test1, meme8_rect1)
                            if a == (2, 1):
                                meme3_test2 = pygame.image.load('data/meme3.png')
                                meme3_rect2 = meme_test.get_rect(bottomright=(260, 340))
                                Screen.blit(meme3_test2, meme3_rect2)
                            if a == (2, 2):
                                meme1_test2 = pygame.image.load('data/meme1.jpg')
                                meme1_rect2 = meme_test.get_rect(bottomright=(340, 340))
                                Screen.blit(meme1_test2, meme1_rect2)
                            if a == (2, 3):
                                meme7_test2 = pygame.image.load('data/meme7.png')
                                meme7_rect2 = meme_test.get_rect(bottomright=(420, 340))
                                Screen.blit(meme7_test2, meme7_rect2)
                            if a == (3, 0):
                                meme5_test2 = pygame.image.load('data/meme5.jpg')
                                meme5_rect2 = meme_test.get_rect(bottomright=(180, 420))
                                Screen.blit(meme5_test2, meme5_rect2)
                            if a == (3, 1):
                                meme2_test2 = pygame.image.load('data/meme2.jpg')
                                meme2_rect2 = meme_test.get_rect(bottomright=(260, 420))
                                Screen.blit(meme2_test2, meme2_rect2)
                            if a == (3, 2):
                                meme6_test2 = pygame.image.load('data/meme6.png')
                                meme6_rect2 = meme_test.get_rect(bottomright=(340, 420))
                                Screen.blit(meme6_test2, meme6_rect2)
                            if a == (3, 3):
                                meme4_test2 = pygame.image.load('data/meme4.jpg')
                                meme4_rect2 = meme_test.get_rect(bottomright=(420, 420))
                                Screen.blit(meme4_test2, meme4_rect2)
                            if a == (0, 4):
                                meme11_test1 = load_image('meme11.jpg')
                                meme11_rect1 = meme_test.get_rect(bottomright=(500, 180))
                                Screen.blit(meme11_test1, meme11_rect1)
                            if a == (0, 5):
                                meme10_test1 = load_image('meme10.png')
                                meme10_rect1 = meme_test.get_rect(bottomright=(580, 180))
                                Screen.blit(meme10_test1, meme10_rect1)
                            if a == (1, 4):
                                meme9_test2 = load_image('meme9.png')
                                meme9_rect2 = meme_test.get_rect(bottomright=(500, 260))
                                Screen.blit(meme9_test2, meme9_rect2)
                            if a == (1, 5):
                                meme12_test1 = load_image('meme12.jpg')
                                meme12_rect1 = meme_test.get_rect(bottomright=(580, 260))
                                Screen.blit(meme12_test1, meme12_rect1)
                            if a == (2, 4):
                                meme14_test2 = load_image('meme14.png')
                                meme14_rect2 = meme_test.get_rect(bottomright=(500, 340))
                                Screen.blit(meme14_test2, meme14_rect2)
                            if a == (2, 5):
                                meme17_test2 = load_image('meme17.jpg')
                                meme17_rect2 = meme_test.get_rect(bottomright=(580, 340))
                                Screen.blit(meme17_test2, meme17_rect2)
                            if a == (3, 4):
                                meme15_test2 = load_image('meme15.jpg')
                                meme15_rect2 = meme_test.get_rect(bottomright=(500, 420))
                                Screen.blit(meme15_test2, meme15_rect2)
                            if a == (3, 5):
                                meme16_test2 = load_image('meme16.jpg')
                                meme16_rect2 = meme_test.get_rect(bottomright=(580, 420))
                                Screen.blit(meme16_test2, meme16_rect2)
                            if a == (4, 4):
                                meme10_test2 = load_image('meme10.png')
                                meme10_rect2 = meme_test.get_rect(bottomright=(500, 500))
                                Screen.blit(meme10_test2, meme10_rect2)
                            if a == (4, 5):
                                meme9jpg_test2 = load_image('meme9.jpg')
                                meme9jpg_rect2 = meme_test.get_rect(bottomright=(580, 500))
                                Screen.blit(meme9jpg_test2, meme9jpg_rect2)
                            if a == (5, 4):
                                meme17_test1 = load_image('meme17.jpg')
                                meme17_rect1 = meme_test.get_rect(bottomright=(500, 580))
                                Screen.blit(meme17_test1, meme17_rect1)
                            if a == (5, 5):
                                meme13_test1 = load_image('meme13.jpg')
                                meme13_rect1 = meme_test.get_rect(bottomright=(580, 580))
                                Screen.blit(meme13_test1, meme13_rect1)
                            if a == (4, 0):
                                meme9_test1 = load_image('meme9.png')
                                meme9_rect1 = meme_test.get_rect(bottomright=(180, 500))
                                Screen.blit(meme9_test1, meme9_rect1)
                            if a == (4, 1):
                                meme13_test2 = load_image('meme13.jpg')
                                meme13_rect2 = meme_test.get_rect(bottomright=(260, 500))
                                Screen.blit(meme13_test2, meme13_rect2)
                            if a == (4, 2):
                                meme9jpg_test1 = load_image('meme9.jpg')
                                meme9jpg_rect1 = meme_test.get_rect(bottomright=(340, 500))
                                Screen.blit(meme9jpg_test1, meme9jpg_rect1)
                            if a == (4, 3):
                                meme11_test2 = load_image('meme11.jpg')
                                meme11_rect2 = meme_test.get_rect(bottomright=(420, 500))
                                Screen.blit(meme11_test2, meme11_rect2)
                            if a == (5, 0):
                                meme14_test1 = load_image('meme14.png')
                                meme14_rect1 = meme_test.get_rect(bottomright=(180, 580))
                                Screen.blit(meme14_test1, meme14_rect1)
                            if a == (5, 1):
                                meme15_test1 = load_image('meme15.jpg')
                                meme15_rect1 = meme_test.get_rect(bottomright=(260, 580))
                                Screen.blit(meme15_test1, meme15_rect1)
                            if a == (5, 2):
                                meme12_test2 = load_image('meme12.jpg')
                                meme12_rect2 = meme_test.get_rect(bottomright=(340, 580))
                                Screen.blit(meme12_test2, meme12_rect2)
                            if a == (5, 3):
                                meme16_test1 = load_image('meme16.jpg')
                                meme16_rect1 = meme_test.get_rect(bottomright=(420, 580))
                                Screen.blit(meme16_test1, meme16_rect1)

                            FIRST_OPPENED = True
                            old = a

                font = pygame.font.Font(None, 50)
                Screen.fill(pygame.Color('grey'), pygame.Rect(0, 0, 300, 80))
                text = font.render("Очки: ", False, 'red')
                text2 = font.render(str(RESULT), False, 'red')
                Screen.blit(text, [20, 20])
                Screen.blit(text2, [150, 20])
                pygame.display.flip()

            pygame.display.flip()
        pygame.quit()


start_screen()

ACTUALL_DIFF = None

# цикл для менюшки

def main():
    pygame.display.set_caption('MEMory Game')
    running = True
    while running:

        def name(value):
            global NAME
            NAME = value
            print(NAME)
            return NAME

        def set_difficulty(value, difficulty):
            global ACTUALL_DIFF
            ACTUALL_DIFF = value[1]
            return ACTUALL_DIFF

        def start_the_game():
            diff = ACTUALL_DIFF
            game(diff)

        menu = pygame_menu.Menu('Добро пожаловать', 800, 600,
                                theme=pygame_menu.themes.THEME_DEFAULT)

        menu.add.text_input('Ваше имя :', default='User', onreturn=name, maxchar=10)
        menu.add.selector('Сложность :', [('Легкая', 1), ('Сложная', 2)], onchange=set_difficulty)
        menu.add.button('Играть', start_the_game)
        menu.add.button('Выйти', pygame_menu.events.EXIT)

        menu.mainloop(Screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == '__main__':
    main()
