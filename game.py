import pygame, os, sys

FPS = 60
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
BOX_SIZE = 30
BETWEEN_BOX = 15

BGCOLOR = pygame.Color("BLUE")
BOXCOLOT = pygame.Color("WHITE")

Screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
clock = pygame.time.Clock()


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



