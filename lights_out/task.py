"""Выключи свет: нажатие на клетку переключает её и соседей по стороне, нужно погасить все лампы."""

import random
from itertools import product

from sirius_gate import FamilyCard, TaskFamily, Transition, blocks, required_text

SIZES = {1: 3, 2: 3, 3: 4, 4: 4, 5: 5}
SCRAMBLE = {1: 2, 2: 4, 3: 4, 4: 7, 5: 9}
# На поле 4×4 разные наборы нажатий дают одно и то же, поэтому длину решения проверяем отдельно.
SHORTEST = {1: 2, 2: 3, 3: 4, 4: 5, 5: 7}


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


def public_state(private_state):
    lamps = private_state["lamps"]
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
            blocks.facts(f"Нажатий: {len(private_state['presses'])}", f"Горит ламп: {sum(map(sum, lamps))}"),
        ],
        commands=["op", "undo", "reset", "done"],
        help_lines=[
            "/op press:<строка>:<столбец> — нажать клетку, счёт с нуля",
            "/undo — отменить последнее нажатие",
            "/reset — вернуть исходное поле",
            "done — все лампы погашены",
        ],
        response_hint="done",
        answer_guide="Когда все лампы погашены, напишите в чате done.",
    )


def generate(seed, difficulty, context):
    rng = random.Random(seed)
    size = SIZES[difficulty]
    cells = [(row, col) for row in range(size) for col in range(size)]
    while True:
        lamps = [[0] * size for _ in range(size)]
        for row, col in rng.sample(cells, SCRAMBLE[difficulty]):
            press(lamps, row, col)
        optimal = len(shortest_solution(lamps))
        if optimal >= SHORTEST[difficulty]:
            break
    private = {"start": [line[:] for line in lamps], "lamps": lamps, "presses": [], "optimal": optimal}
    return public_state(private), private


def transition(private_state, accepted, reason, message, normalized=""):
    return Transition(
        public_state=public_state(private_state),
        private_state=private_state,
        accepted=accepted,
        reason=reason,
        message=message,
        normalized_input=normalized,
    )


def apply_press(payload, public, private_state):
    command = required_text(payload, "op_id", "Нужно указать клетку.")
    parts = command.split(":")
    size = len(private_state["lamps"])
    valid = len(parts) == 3 and parts[0] == "press" and all(part.isdigit() and int(part) < size for part in parts[1:])
    if not valid:
        return transition(private_state, False, "unknown_cell", "Такой клетки на поле нет.", command)
    row, col = int(parts[1]), int(parts[2])
    state = {**private_state, "lamps": [line[:] for line in private_state["lamps"]]}
    press(state["lamps"], row, col)
    state["presses"] = [*private_state["presses"], [row, col]]
    return transition(state, True, "accepted", "Клетка нажата.", command)


def undo(payload, public, private_state):
    if not private_state["presses"]:
        return transition(private_state, False, "nothing_to_undo", "Отменять нечего.")
    row, col = private_state["presses"][-1]
    state = {**private_state, "lamps": [line[:] for line in private_state["lamps"]]}
    press(state["lamps"], row, col)
    state["presses"] = private_state["presses"][:-1]
    return transition(state, True, "accepted", "Последнее нажатие отменено.")


def reset(payload, public, private_state):
    state = {**private_state, "lamps": [line[:] for line in private_state["start"]], "presses": []}
    return transition(state, True, "accepted", "Поле возвращено в исходное состояние.")


def evaluate(answer, private_state):
    if any(map(any, private_state["lamps"])):
        return {"correct": False, "should_finalize": False, "feedback": "Ещё не все лампы погашены."}
    used = len(private_state["presses"])
    return {
        "correct": True,
        "presses": used,
        "optimal": private_state["optimal"],
        "efficient": used <= private_state["optimal"],
        "continuous_score": private_state["optimal"] / max(used, private_state["optimal"]),
    }


def reference_answer(private_state):
    moves = shortest_solution(private_state["lamps"])
    return "done", [f"/op press:{row}:{col}" for row, col in moves]


FAMILY = TaskFamily(
    key="lights_out",
    version="lights-out-v1",
    generate=generate,
    evaluate=evaluate,
    actions={"apply_op": apply_press, "undo": undo, "reset": reset},
    reference_answer=reference_answer,
    card=FamilyCard(
        title="Выключи свет",
        description="Поле ламп, где нажатие переключает клетку и её соседей. Задача линейной алгебры над полем из двух элементов.",
    ),
)
