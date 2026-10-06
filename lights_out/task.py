"""Выключи свет: нажатие на клетку переключает её и соседей по стороне, нужно погасить все лампы."""

from itertools import product

from sirius_gate import EASY, HARD, MEDIUM, NotYet, Plugin, Rejected, TaskType, answers, blocks

SIZES = {EASY: 3, MEDIUM: 4, HARD: 5}
SCRAMBLE = {EASY: 3, MEDIUM: 5, HARD: 9}
# На поле 4×4 разные наборы нажатий дают одно и то же, поэтому длину решения проверяет validate.
SHORTEST = {EASY: 2, MEDIUM: 4, HARD: 6}


def press(lamps, row, col):
    size = len(lamps)
    for r, c in ((row, col), (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
        if 0 <= r < size and 0 <= c < size:
            lamps[r][c] ^= 1


def shortest_solution(lamps):
    """Нажатия, гасящие поле, в наименьшем числе. Первая строка перебирается, остальные вынуждены."""
    size = len(lamps)
    best = None
    for first_row in product((0, 1), repeat=size):
        field = [row[:] for row in lamps]
        presses = []
        for col, chosen in enumerate(first_row):
            if chosen:
                press(field, 0, col)
                presses.append((0, col))
        for row in range(1, size):
            for col in range(size):
                if field[row - 1][col]:
                    press(field, row, col)
                    presses.append((row, col))
        if not any(field[-1]) and (best is None or len(presses) < len(best)):
            best = presses
    return best


def generate(level, rng):
    size = SIZES[level]
    lamps = [[0] * size for _ in range(size)]
    cells = [(row, col) for row in range(size) for col in range(size)]
    for row, col in rng.sample(cells, SCRAMBLE[level]):
        press(lamps, row, col)
    return {"level": level, "lamps": lamps, "presses": 0, "optimal": len(shortest_solution(lamps))}


def validate(variant):
    """Вариант годится, если короче заданного числа нажатий его не решить."""
    return variant["optimal"] >= SHORTEST[variant["level"]]


def view(variant):
    lamps = variant["lamps"]
    cells = [
        [
            blocks.cell("●" if lit else "", tone="accent" if lit else "plain", command=f"/op press:{row}:{col}")
            for col, lit in enumerate(line)
        ]
        for row, line in enumerate(lamps)
    ]
    return blocks.scene(
        "Нажатие на клетку переключает её и соседние по стороне клетки. Погасите все лампы. "
        "Чем меньше нажатий, тем лучше.",
        [
            blocks.grid(cells),
            blocks.facts(f"Нажатий: {variant['presses']}", f"Горит ламп: {sum(map(sum, lamps))}"),
        ],
        commands=["done"],
        help_lines=[
            "/op press:<строка>:<столбец> — нажать клетку, счёт с нуля",
            "done — все лампы погашены",
        ],
        response_hint="done",
        answer_guide="Когда все лампы погашены, напишите в чате done.",
    )


def move(variant, text):
    """Ход участника: команда /op press:<строка>:<столбец> или клик по клетке."""
    parts = text.split(":")
    size = len(variant["lamps"])
    if len(parts) != 3 or parts[0] != "press" or not all(part.isdigit() and int(part) < size for part in parts[1:]):
        raise Rejected("Такой клетки на поле нет.")
    press(variant["lamps"], int(parts[1]), int(parts[2]))
    variant["presses"] += 1
    return variant, "Клетка нажата."


def check(answer, variant):
    if answers.text(answer) != "done":
        return False
    if any(map(any, variant["lamps"])):
        raise NotYet("Ещё не все лампы погашены.")
    used, optimal = variant["presses"], variant["optimal"]
    return {"correct": True, "presses": used, "optimal": optimal, "continuous_score": optimal / max(used, optimal)}


def solution(variant):
    moves = shortest_solution(variant["lamps"])
    return "done", [f"/op press:{row}:{col}" for row, col in moves]


PLUGIN = Plugin(
    name="lights_out",
    version="1.0",
    author="Sirius Gate",
    description="Поле ламп, где нажатие переключает клетку и её соседей. "
    "Задача линейной алгебры над полем из двух элементов.",
    task_types=[
        TaskType(
            key="lights_out",
            title="Выключи свет",
            generate=generate,
            validate=validate,
            check=check,
            view=view,
            move=move,
            solution=solution,
        )
    ],
)
