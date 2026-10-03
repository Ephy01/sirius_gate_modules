"""Сколько путей ведёт из левого верхнего угла в правый нижний, если ходить только вправо и вниз."""

import random

from sirius_gate import FamilyCard, TaskFamily, answers, blocks

# На каждой сложности размер поля выбирается из нескольких, иначе вариантов слишком мало.
SIZES = {
    1: [(3, 4), (4, 3), (4, 4)],
    2: [(4, 4), (4, 5), (5, 4)],
    3: [(4, 5), (5, 5), (5, 4)],
    4: [(5, 6), (6, 5), (6, 6)],
    5: [(6, 7), (7, 6), (7, 7)],
}


def count_paths(rows, cols, blocked):
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


def generate(seed, difficulty, context):
    rng = random.Random(seed)
    rows, cols = rng.choice(SIZES[difficulty])
    inner = [(row, col) for row in range(rows) for col in range(cols) if (row, col) not in {(0, 0), (rows - 1, cols - 1)}]
    while True:
        blocked = set(rng.sample(inner, difficulty + 1))
        answer = count_paths(rows, cols, blocked)
        if answer >= 2:
            break

    def draw(row, col):
        if (row, col) == (0, 0):
            return blocks.cell("С", tone="accent")
        if (row, col) == (rows - 1, cols - 1):
            return blocks.cell("Ф", tone="accent")
        return blocks.cell("✕", tone="muted") if (row, col) in blocked else blocks.cell()

    public = blocks.scene(
        "Фишка стоит в клетке С и за один ход сдвигается на одну клетку вправо или вниз. "
        "В клетки с крестиком заходить нельзя. Сколькими способами можно дойти до клетки Ф?",
        [blocks.grid([[draw(row, col) for col in range(cols)] for row in range(rows)])],
        response_hint="/answer <число способов>",
    )
    return public, {"answer": answer}


def evaluate(answer, private_state):
    number = answers.integer(answer)
    return {"correct": number == private_state["answer"], "parsed": number is not None}


FAMILY = TaskFamily(
    key="lattice_paths",
    version="lattice-paths-v1",
    generate=generate,
    evaluate=evaluate,
    reference_answer=lambda private_state: (f"/answer {private_state['answer']}", []),
    card=FamilyCard(
        title="Пути на клетчатом поле",
        description="Подсчёт путей фишки, которая ходит вправо и вниз и обходит запрещённые клетки.",
    ),
)
