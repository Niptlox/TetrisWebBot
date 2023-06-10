from collections import defaultdict

figure_rotations_I = {0: ((-1, 0), (0, 0), (1, 0), (2, 0)),
                      90: ((1, -1), (1, 0), (1, 1), (1, 2)),
                      180: ((-1, 1), (0, 1), (1, 1), (2, 1)),
                      270: ((0, -1), (0, 0), (0, 1), (0, 2)), }

square = ((0, 0), (0, 1), (1, 0), (1, 1))
_figures_lr = {
    ((0, 0), (1, 0), (1, 1), (2, 1)): "Z",
    ((0, 1), (1, 0), (1, 1), (2, 0)): "S",
    ((0, 0), (1, 0), (2, 0), (3, 0)): "I",
    ((0, 1), (1, 0), (1, 1), (2, 1)): "T",
    # ((0, 1), (1, 0), (2, 0), (2, 1)): ((-1, 1), (0, 0), (1, 0), (1, 1)),
    ((0, 1), (1, 1), (2, 0), (2, 1)): "L",
    ((0, 0), (0, 1), (1, 1), (2, 1)): "J",
    square: "O"
}
figures_lr = {tuple(sorted(k)): v for k, v in _figures_lr.items()}
figures = {
    "I": ((-1, 0), (0, 0), (1, 0), (2, 0)),
    "J": ((-1, -1), (-1, 0), (0, 0), (1, 0)),
    "L": ((-1, 0), (0, 0), (1, -1), (1, 0)),
    "O": ((0, -1), (0, 0), (1, -1), (1, 0)),
    "S": ((-1, 0), (0, -1), (0, 0), (1, -1)),
    "T": ((-1, 0), (0, -1), (0, 0), (1, 0)),
    "Z": ((-1, -1), (0, -1), (0, 0), (1, 0))
}


def get_player_figure_at_field(field: list):
    if type(field) is dict:
        field = dict_field_to_array(field)
    _fig_points = list()

    minx, miny = 1e9, 1e9

    field_w = len(field[0])
    if any(field[3]):
        return (minx, miny), [None, None]
    for iy in range(2):
        for ix in range(field_w):
            if field[iy][ix] is not None:
                _fig_points.append((ix, iy))
                minx = min(minx, ix)
                miny = min(miny, iy)
    _fig_points = tuple(sorted((ix - minx, iy - miny) for ix, iy in _fig_points))
    # print("_fig_points", _fig_points)
    fig_key = figures_lr.get(_fig_points, None)
    fig_points = figures.get(fig_key)
    offsety = offsetx = 0
    if fig_points:
        offsetx = fig_points[0][0] - _fig_points[0][0]
        offsety = fig_points[0][1] - _fig_points[0][1]
    return (minx - offsetx, miny - offsety), (fig_key, fig_points)


def collide(field, figure, pos):
    for px, py in figure[1]:
        x, y = pos[0] + px, pos[1] + py
        if x < 0 or x >= len(field[0]) or y >= len(field):
            return True
        if y >= 0 and field[y][x] is not None:
            return True


def rotate_right90(figure, current_angle):
    if figure[0] == "O":
        return figure, current_angle
    current_angle = (current_angle + 90) % 360
    if figure[0] == "I":
        return (figure[0], figure_rotations_I[current_angle]), current_angle
    return (figure[0], tuple((-y, x) for x, y in figure[1])), current_angle


def get_move_score(field, figure, pos):
    mscore = 100
    maxy = 0
    field_h = len(field)
    _figure = sorted(figure[1], key=lambda p: p[1], reverse=True)
    fig_columns = {}
    for px, py in _figure:
        if px not in fig_columns:
            fig_columns[px] = py
    for px in fig_columns:
        py = fig_columns[px]
        x, y = pos[0] + px, pos[1] + py
        maxy = max(maxy, y)
        if (y + 1) >= field_h or field[y + 1][x] is not None:
            mscore += 1
        else:
            for y1 in range(y + 1, field_h):
                mscore -= 1
                if field[y + 1][x] is not None:
                    break

    mscore += maxy * 1000
    return mscore


def figure_at_pos(figure, pos):
    return [(pos[0] + px, pos[1] + py) for px, py in figure[1]]


def dict_field_to_array(d_field, field_w=10, field_h=20):
    field = [[None] * field_w for _ in range(field_h)]
    for pos, color in d_field.items():
        field[pos[1]][pos[0]] = color
    return field


def get_best_move(field, start_figure, start_pos, start_angle, next_figure):
    if type(field) is dict:
        field = dict_field_to_array(field, field_w=10, field_h=20)
    field_w, field_h = len(field[0]), len(field)
    # [move_score, x, cnt_rotations, result_points]
    best_move = [-1, 0, 0, []]
    for k in range(4):
        figure = list(start_figure)
        angle = start_angle
        for _ in range(k):
            figure, angle = rotate_right90(figure, angle)
        for ix in range(field_w):
            if collide(field, figure, [ix, start_pos[1]]):
                continue
            for iy in range(start_pos[1], field_h):
                if collide(field, figure, [ix, iy]):
                    pos = [ix, iy - 1]
                    move_score = get_move_score(field, figure, pos)
                    if move_score > best_move[0]:
                        best_move = [move_score, ix, k, figure_at_pos(figure, pos)]
                    break
    return best_move
