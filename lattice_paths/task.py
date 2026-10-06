"""Сколько путей ведёт из левого верхнего угла в правый нижний, если ходить только вправо и вниз."""

from sirius_gate import EASY, HARD, MEDIUM, Plugin, TaskType, answers, blocks

# На каждом уровне размер поля выбирается из нескольких, иначе вариантов слишком мало.
SIZES = {
    EASY: [(3, 4), (4, 3), (4, 4)],
    MEDIUM: [(4, 5), (5, 5), (5, 4)],
    HARD: [(6, 7), (7, 6), (7, 7)],
}
BLOCKED = {EASY: 2, MEDIUM: 4, HARD: 6}


def count_paths(variant):
    rows, cols = variant["rows"], variant["cols"]
    blocked = {tuple(cell) for cell in variant["blocked"]}
    ways = [[0] * cols for _ in range(rows)]
    ways[0][0] = 1
    for row in range(rows):
        for col in range(cols):
            if (row, col) in blocked:
                ways[row][col] = 0
                continue
            if row > 0:
                ways[row][col] += ways[row - 1][col]
            if col > 0:
                ways[row][col] += ways[row][col - 1]
    return ways[-1][-1]


def generate(level, rng):
    rows, cols = rng.choice(SIZES[level])
    corners = {(0, 0), (rows - 1, cols - 1)}
    inner = [[row, col] for row in range(rows) for col in range(cols) if (row, col) not in corners]
    return {"rows": rows, "cols": cols, "blocked": rng.sample(inner, BLOCKED[level])}


def validate(variant):
    """Вариант годится, если до финиша можно дойти хотя бы двумя способами."""
    return count_paths(variant) >= 2


def view(variant):
    rows, cols = variant["rows"], variant["cols"]
    blocked = {tuple(cell) for cell in variant["blocked"]}

    def draw(row, col):
        if (row, col) == (0, 0):
            return blocks.cell("С", tone="accent")
        if (row, col) == (rows - 1, cols - 1):
            return blocks.cell("Ф", tone="accent")
        return blocks.cell("✕", tone="muted") if (row, col) in blocked else blocks.cell()

    return blocks.scene(
        "Фишка стоит в клетке С и за один ход сдвигается на одну клетку вправо или вниз. "
        "В клетки с крестиком заходить нельзя. Сколькими способами можно дойти до клетки Ф?",
        [blocks.grid([[draw(row, col) for col in range(cols)] for row in range(rows)])],
        response_hint="/answer <число способов>",
    )


def check(answer, variant):
    return answers.integer(answer) == count_paths(variant)


def solution(variant):
    return f"/answer {count_paths(variant)}"


PLUGIN = Plugin(
    name="lattice_paths",
    version="1.0",
    author="Sirius Gate",
    description="Подсчёт путей фишки, которая ходит вправо и вниз и обходит запрещённые клетки.",
    task_types=[
        TaskType(
            key="lattice_paths",
            title="Пути на клетчатом поле",
            generate=generate,
            validate=validate,
            check=check,
            view=view,
            solution=solution,
        )
    ],
)
