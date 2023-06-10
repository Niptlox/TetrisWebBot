import pygame as pg

MSIZE = (10, 20)
square = ((0, 0), (0, 1), (1, 0), (1, 1))
_figures = {
    ((0, 0), (1, 0), (1, 1), (2, 1)): ((-1, -1), (0, 0), (0, -1), (1, 0)),
    ((0, 1), (1, 0), (1, 1), (2, 0)): ((-1, 0), (0, 0), (0, -1), (1, -1)),
    ((0, 0), (1, 0), (2, 0), (3, 0)): ((-2, 0), (-1, 0), (0, 0), (1, 0)),
    ((0, 1), (1, 0), (1, 1), (2, 1)): ((-1, 0), (0, -1), (0, 0), (1, 0)),
    # ((0, 1), (1, 0), (2, 0), (2, 1)): ((-1, 1), (0, 0), (1, 0), (1, 1)),
    ((0, 1), (1, 1), (2 , 0), (2, 1)): ((-1, 0), (0, 0), (1, -1), (1, 0)),
    ((0, 0), (0, 1), (1, 1), (2, 1)): ((-1, -1), (-1, 0), (0, 0), (1, 0)),
    square: square
}
figures_centred = {}
figures = {tuple(sorted(k)): tuple(sorted(v)) for k, v in _figures.items()}


def get_player_figure_at_field(field: dict):
    _fig_points = list()

    minx, miny = 1e9, 1e9
    for ix in range(MSIZE[0]):
        if field.get((ix, 3)) is not None:
            return (minx, miny), None
    for iy in range(2):
        for ix in range(MSIZE[0]):
            if field.get((ix, iy)) is not None:
                _fig_points.append((ix, iy))
                minx = min(minx, ix)
                miny = min(miny, iy)
    _fig_points = tuple(sorted((ix - minx, iy - miny) for ix, iy in _fig_points))
    # print("_fig_points", _fig_points)
    fig_points = figures.get(_fig_points, None)
    offsety = offsetx = 0
    if fig_points:
        offsetx = fig_points[0][0] - _fig_points[0][0]
        offsety = fig_points[0][1] - _fig_points[0][1]
    return (minx - offsetx, miny - offsety), fig_points


def rotate_right90(points):
    # x, y => -y, x
    print(points, [(-p[1], p[0]) for p in points])
    return [(-p[1], p[0]) for p in points]


def check_collide(_player_figure, _pos, field):
    for point in _player_figure:
        x, y = _pos[0] + point[0], _pos[1] + point[1]
        if (x, y) in field or not (0 <= x < MSIZE[0] and 0 <= y < MSIZE[1]):
            return True
    return False


K_SPEED = 0
K_LEFT = 1
K_RIGHT = 2
K_ROTATE = 3


def player_step(key):
    if key == K_SPEED:
        pass
    elif key == K_LEFT:
        pass
    elif key == K_RIGHT:
        pass
    elif key == K_ROTATE:
        pass


first = True


def step_q(fig, _pos, field):
    min_y = min([_pos[1] + p[1] for p in fig])
    max_y = max([_pos[1] + p[1] for p in fig])
    s = get_fig_contact_area(fig, _pos, field)
    return max_y, s + len([1 for p in fig if (_pos[1] + p[1]) == max_y])


def get_fig_contact_area(fig, _pos, field):
    s = 0
    for p in fig:
        x, y = p[0] + _pos[0], p[1] + _pos[1]
        s += bool(field.get((x + 1, y))) + bool(field.get((x - 1, y))) + bool(field.get((x, y + 1)))
    return s


def compare_q(q1, q2):
    # if q1[1] > q2[1] or q1[0] > q2[0]:
    #     return True
    if q1[0] > q2[0] or (q1[0] == q2[0] and q1[1] > q2[1]):
        return True
    return False


def smartbot(field, player_figure, start_y=2):
    # maxy, x, rotates
    best = (-1, 0, 0)
    print("y", start_y)
    for x in range(MSIZE[0]):
        print("x", x)
        for k in range(3):
            fig = player_figure
            print("k", k)
            for i in range(k):
                fig = rotate_right90(fig)

            if check_collide(fig, (x, start_y), field):
                print("BREAK")
                break
            for iy in range(1, MSIZE[1]):
                y = start_y + iy
                if check_collide(fig, (x, y), field):
                    q = step_q(fig, (x, y - 1), field)
                    if best[0] == -1 or compare_q(q, best[0]):
                        best = (q, x, k)
                    break
    return best


if __name__ == '__main__':
    WSIZE = (440, 500)
    pg_screen = pg.display.set_mode(WSIZE)
    k = 10
    sur = pg.Surface((k, k))
    sur.fill("white")
    mx, my = 20, 20
    for _fig, fig in figures.items():
        for x, y in _fig:
            pg.draw.rect(pg_screen, "white", ((x * k + mx, y * k + my), (k, k)))
            # if x == 0 and y == 0:
            #     pg.draw.rect(pg_screen, "red", ((x * k + mx, y * k + my), (k, k)))
        for x, y in fig:
            pg.draw.rect(pg_screen, "white", ((x * k + mx + 150, y * k + my), (k, k)))
            if x == 0 and y == 0:
                pg.draw.rect(pg_screen, "red", ((x * k + mx+150, y * k + my), (k, k)))

        my += 50
    pg.display.flip()
    while 1:
        pg.event.get()
