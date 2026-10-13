"""Сколько узлов решётки лежит строго внутри многоугольника с вершинами в узлах."""

from math import atan2, gcd

from sirius_gate import Plugin, TaskType, answers, blocks

SIZES = {1: 5, 2: 6, 3: 7, 4: 8, 5: 9}
VERTICES = {1: 3, 2: 4, 3: 4, 4: 5, 5: 6}
NAMES = "ABCDEF"


def generate(level, rng):
    size = SIZES[level]
    nodes = [[x, y] for x in range(size + 1) for y in range(size + 1)]
    points = rng.sample(nodes, VERTICES[level])
    # Обход вершин вокруг их центра даёт многоугольник без самопересечений.
    center_x = sum(x for x, _ in points) / len(points)
    center_y = sum(y for _, y in points) / len(points)
    points.sort(key=lambda point: atan2(point[1] - center_y, point[0] - center_x))
    return {"size": size, "points": points}


def sides(points):
    return list(zip(points, points[1:] + points[:1]))


def doubled_area(points):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in sides(points)))


def boundary_nodes(points):
    return sum(gcd(x2 - x1, y2 - y1) for (x1, y1), (x2, y2) in sides(points))


def inner_nodes(points):
    """Формула Пика: площадь равна числу внутренних узлов плюс половина граничных минус один."""
    return (doubled_area(points) - boundary_nodes(points) + 2) // 2


def validate(variant):
    """Годится многоугольник без вырожденных углов, внутри которого есть хотя бы два узла."""
    points = variant["points"]
    count = len(points)
    total_x, total_y = sum(x for x, _ in points), sum(y for _, y in points)
    rays = [(count * x - total_x, count * y - total_y) for x, y in points]
    for index, (ax, ay) in enumerate(rays):
        for bx, by in rays[index + 1 :]:
            if ax * by == ay * bx and ax * bx + ay * by > 0:
                return False
    for (x1, y1), (x2, y2), (x3, y3) in zip(points, points[1:] + points[:1], points[2:] + points[:2]):
        if (x2 - x1) * (y3 - y2) == (y2 - y1) * (x3 - x2):
            return False
    return inner_nodes(points) >= 2


def view(variant):
    size, points = variant["size"], variant["points"]
    return blocks.scene(
        "Вершины многоугольника лежат в узлах клетчатой решётки. "
        "Сколько узлов решётки лежит строго внутри многоугольника?",
        [
            blocks.picture(
                [
                    blocks.polygon(points, tone="accent"),
                    *(blocks.point(x, y, label=NAMES[index]) for index, (x, y) in enumerate(points)),
                ],
                x=(-0.5, size + 0.5),
                y=(-0.5, size + 0.5),
                grid=True,
            )
        ],
        response_hint="/answer <число узлов>",
    )


def check(answer, variant):
    return answers.integer(answer) == inner_nodes(variant["points"])


def solution(variant):
    return f"/answer {inner_nodes(variant['points'])}"


PLUGIN = Plugin(
    name="lattice_polygon",
    version="1.0",
    author="Sirius Gate",
    description="Подсчёт узлов решётки внутри многоугольника. Решается формулой Пика или прямым подсчётом.",
    task_types=[
        TaskType(
            key="lattice_polygon",
            title="Узлы внутри многоугольника",
            generate=generate,
            validate=validate,
            check=check,
            view=view,
            solution=solution,
        )
    ],
)
