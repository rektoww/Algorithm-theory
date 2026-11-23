from collections.abc import Iterator

from .errors import InputError


def multiples_of_three(a: int = -100) -> Iterator[int]:
    if type(a) is not int:
        raise InputError("Начальное значение a должно быть целым числом.")

    # Находим первое число >= a, кратное трём.
    # Выражение -a % 3 вычисляет необходимое смещение (0, 1 или 2).
    value = a + (-a % 3)

    # Бесконечный ленивый генератор: числа выдаются по запросу.
    # В интерфейсе их количество ограничивается через islice().
    while True:
        yield value
        value += 3
