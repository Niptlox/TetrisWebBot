import mouse
import keyboard
import pyautogui


def get_mouse_pos():
    p = pyautogui.position()
    return p.x, p.y


def get_rect_with_mouse():
    return get_pos_on_screen(), get_pos_on_screen()


def get_pos_on_screen():
    print("get pos")
    pos1 = None
    while not pos1:
        # print("wa")
        mouse.wait(mouse.LEFT, target_types=mouse.DOWN)
        if keyboard.is_pressed("ctrl"):
            # print("cc", get_mouse_pos(), "p", pos1)
            pos1 = get_mouse_pos()
    return pos1


