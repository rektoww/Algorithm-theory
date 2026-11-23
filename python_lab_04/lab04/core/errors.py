from threading import Event


# Собственные исключения приложения:
# InputError — некорректные параметры,
# Cancelled — остановка вычислений пользователем.
# Оба наследуются от общего LabError.

class LabError(Exception):
    """Ошибка, для которой есть сообщение пользователю."""


class InputError(LabError):
    pass


class Cancelled(LabError):
    pass


# Event из модуля threading. Специальный объект-флаг, который можно менять из одного потока и проверять из другого
def check_cancelled(cancel: Event | None) -> None:
    if cancel is not None and cancel.is_set():
        raise Cancelled("Операция остановлена по запросу пользователя.")


# Преобразуем текст в целое число.
# При ошибке заменяем ValueError на понятный пользователю InputError, сохраняя исходную причину через from exc.
def parse_integer(text: str, label: str) -> int:
    try:
        return int(text)
    except ValueError as exc:
        raise InputError(f"{label}. Введите целое число.") from exc

# Проверяем точный тип int и допустимый диапазон.
# Строгая проверка типа исключает bool, который наследуется от int.
def check_range(value: int, low: int, high: int, label: str) -> None:
    if type(value) is not int or not low <= value <= high:
        raise InputError(f"{label}. Укажите целое число от {low} до {high}.")
