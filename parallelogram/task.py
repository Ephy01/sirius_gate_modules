"""Достройте параллелограмм: точку D нужно перетащить на её место."""

from sirius_gate import Plugin, Rejected, TaskType, answers, blocks

SIZES = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}


def generate(level, rng):
    size = SIZES[level]
    nodes = [[x, y] for x in range(size + 1) for y in range(size + 1)]
    a, b, c, start = rng.sample(nodes, 4)
    return {"level": level, "size": size, "a": a, "b": b, "c": c, "d": start}


def fourth_vertex(variant):
    """В параллелограмме ABCD диагонали делятся пополам, поэтому D = A + C - B."""
    a, b, c = variant["a"], variant["b"], variant["c"]
    return [a[0] + c[0] - b[0], a[1] + c[1] - b[1]]


def validate(variant):
    a, b, c, size = variant["a"], variant["b"], variant["c"], variant["size"]
    target = fourth_vertex(variant)
    area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    # Слишком узкий параллелограмм трудно разглядеть, поэтому площадь ограничена снизу.
    if abs(area) < size or not all(0 <= value <= size for value in target):
        return False
    if target in (a, b, c, variant["d"]):
        return False
    # На первых двух уровнях сторона AB горизонтальна, дальше сторон вдоль осей нет.
    flat = [a[1] == b[1], b[1] == c[1], a[0] == b[0], b[0] == c[0]]
    return flat[0] if variant["level"] <= 2 else not any(flat)


def view(variant):
    a, b, c, d, size = (variant[key] for key in ("a", "b", "c", "d", "size"))
    return blocks.scene(
        "Перетащите точку D так, чтобы ABCD стал параллелограммом. Вершины идут по порядку: A, B, C, D.",
        [
            blocks.picture(
                [
                    blocks.polygon([a, b, c, d], tone="muted", filled=False),
                    blocks.point(*a, label="A"),
                    blocks.point(*b, label="B"),
                    blocks.point(*c, label="C"),
                    blocks.point(*d, label="D", tone="good", drag="D"),
                ],
                x=(-0.5, size + 0.5),
                y=(-0.5, size + 0.5),
                grid=True,
            )
        ],
        commands=["done"],
        response_hint="done",
        answer_guide="Когда точка D стоит на месте, напишите в чате done.",
    )


def drag(variant, name, x, y):
    """Участник перенёс точку: платформа уже поставила её в узел решётки внутри рисунка."""
    if [x, y] in (variant["a"], variant["b"], variant["c"]):
        raise Rejected("Точка D не может совпадать с другой вершиной.")
    variant["d"] = [x, y]
    return variant, f"Точка D теперь в ({x}, {y})."


def check(answer, variant):
    return answers.text(answer) == "done" and variant["d"] == fourth_vertex(variant)


def solution(variant):
    x, y = fourth_vertex(variant)
    return "done", [f"/op drag:D:{x}:{y}"]


PLUGIN = Plugin(
    name="parallelogram",
    version="1.0",
    author="Sirius Gate",
    description="Четвёртая вершина параллелограмма на клетчатой решётке. Точку нужно перетащить.",
    task_types=[
        TaskType(
            key="parallelogram",
            title="Достройте параллелограмм",
            generate=generate,
            validate=validate,
            check=check,
            view=view,
            drag=drag,
            solution=solution,
        )
    ],
)
