import os.path
import time

import keyboard
import numpy
import numpy as np
import pyautogui

from PIL import ImageGrab
import mss
import cv2
import pygame as pg
import getMouseRect
from smartbot import *
from TetrisBot import get_best_move, get_player_figure_at_field

# screen record object
sct = mss.mss()

FPS = 60
TSIDE = 25
WSIZE = (440, 500)
pg_screen = pg.display.set_mode(WSIZE)


class Joystick:
    @classmethod
    def press(cls, key, cnt=1):
        for i in range(cnt):
            keyboard.press_and_release(key)
            time.sleep(0.05)

    @classmethod
    def right(cls, cnt=1):
        cls.press("right", cnt)

    @classmethod
    def left(cls, cnt=1):
        cls.press("left", cnt)

    @classmethod
    def space(cls, cnt=1):
        cls.press("space", cnt)

    @classmethod
    def rotate_r90(cls, cnt=1):
        cls.press("up", cnt)


def rect_size(rect):
    if len(rect) == 4:
        rect = rect[0:2], rect[2:4]
    return rect[1][0] - rect[0][0], rect[1][1] - rect[0][1]


def crop(im, rect):
    if len(rect) == 4:
        rect = rect[0:2], rect[2:4]
    return im[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]


def bbox(a: np.ndarray):
    a = np.array(a)[:,:,:3]  # keep RGB only
    # print(a)
    m = np.any(a != [255, 255, 255], axis=2)
    coords = np.argwhere(m)
    y0, x0, y1, x1 = *np.min(coords, axis=0), *np.max(coords, axis=0)
    return (x0, y0), (x1 + 1, y1 + 1)


def get_screen(screen_rect: dict=None):
    if screen_rect is None:
        w, h = pyautogui.size()
        screen_rect = (0, 0, w, h)
    # printscreen_pil = ImageGrab.grab()
    # printscreen_numpy = np.array(printscreen_pil.getdata(), dtype='uint8') \
    #     .reshape((printscreen_pil.size[1], printscreen_pil.size[0], 3))
    printscreen_numpy = numpy.asarray(sct.grab(screen_rect))
    return printscreen_numpy


def get_area_rect():
    rect = getMouseRect.get_rect_with_mouse()
    # print("mrect", rect, rect_size(rect))
    printscreen_numpy = get_screen()
    # cv2.imshow('window', printscreen_numpy)
    cv2.imwrite("screenshots/img.png", printscreen_numpy)
    pre_img = crop(printscreen_numpy, rect)
    cv2.imwrite("screenshots/crop_img.png", pre_img)
    brect = bbox(pre_img)
    # print("brect", brect)
    b_img = crop(pre_img, brect)
    # cv2.imwrite("screenshots/b_img.png", b_img)

    field_rect = (rect[0][0] + brect[0][0], rect[0][1] + brect[0][1]), (
        rect[0][0] + brect[1][0], rect[0][1] + brect[1][1])
    return field_rect


def get_field_rect():
    fname = "cash/field_rect.data"
    if os.path.exists(fname):
        try:
            with open(fname) as f:
                return eval(f.readline())
        except Exception as exc:
            print("Error open cash file", exc)

    print("Please select an area with a field for the game")
    frect = get_area_rect()
    with open(fname, "w") as f:
        f.write(str(frect))
    return frect


def img_show(img):
    cv2.imshow('window', img)


def get_tetris_field_of_image(img: np.ndarray):
    field = {}
    field_size = (10, 20)
    size = img.shape[1], img.shape[0]
    # print(img)
    cell_size = size[0] / field_size[0], size[1] / field_size[1]
    half_size = cell_size[0] // 2
    # print("size", size, cell_size)
    for ix in range(field_size[0]):
        for iy in range(field_size[1]):
            x, y = int(cell_size[0] * ix + half_size), int(cell_size[1] * iy + half_size)
            # print((x, y), img[y][x])
            if not is_gray(img[y][x]):
                field[(ix, iy)] = list(img[y][x])
    return field


def is_gray(color):
    return color[0] == color[1] == color[2]


def activate_steps(steps, x=0):
    if steps[0] != -1:
        offset_x = steps[1] - x
        cnt_rot90 = steps[2]
        Joystick.rotate_r90(cnt_rot90)
        if offset_x > 0:
            Joystick.right(offset_x)
        else:
            Joystick.left(-offset_x)
        time.sleep(0.2)
        Joystick.space()


# is oldest
# def new_step(field):
#     pos, player_figure = get_player_figure_at_field(field)
#     for ix in range(MSIZE[0]):
#         for iy in range(2):
#             if field.get((ix, iy)) is not None:
#                 del field[(ix, iy)]
#     for ixy, cell_color in field.items():
#         x, y = ixy
#         pg.draw.rect(pg_screen, cell_color, (x * TSIDE, y * TSIDE, TSIDE, TSIDE))
#     # pos = (13, 3)
#     # print(player_figure)
#     if player_figure:
#         best_steps = smartbot(field, player_figure, pos[1])
#         print(best_steps)
#         activate_steps(best_steps, x=pos[0])
#         for point in player_figure:
#             x, y = pos[0] + point[0], pos[1] + point[1]
#             pg.draw.rect(pg_screen, "red", (x * TSIDE, y * TSIDE, TSIDE, TSIDE))


def new_move(field):
    pos, player_figure = get_player_figure_at_field(field)
    for ix in range(MSIZE[0]):
        for iy in range(2):
            if field.get((ix, iy)) is not None:
                del field[(ix, iy)]
    for ixy, cell_color in field.items():
        x, y = ixy
        pg.draw.rect(pg_screen, cell_color, (x * TSIDE, y * TSIDE, TSIDE, TSIDE))
    if player_figure[0]:
        best_steps = get_best_move(field, player_figure, pos, 0, [])
        print(best_steps)
        activate_steps(best_steps, x=pos[0])
        for point in player_figure[1]:
            x, y = pos[0] + point[0], pos[1] + point[1]
            pg.draw.rect(pg_screen, "red", (x * TSIDE, y * TSIDE, TSIDE, TSIDE))



def main():
    i = 0
    areafield_rect = get_field_rect()
    # areafield_size = rect_size(areafield_rect)
    # dict_mon_rect = {"top": areafield_rect[0][0], "left": areafield_rect[0][1],
    #                  "width": areafield_size[0], "height": areafield_size[1]}
    while True:
        pg_screen.fill("black")
        screen_img = get_screen()
        f_img = crop(screen_img, areafield_rect)
        img_show(f_img)
        cv2.imwrite("screenshots/ff_img.png", f_img)
        field = get_tetris_field_of_image(f_img)
        # print(field)

        new_move(field)
        pg.display.flip()

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    main()
