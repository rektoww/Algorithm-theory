import re
from dataclasses import dataclass

from .errors import InputError

DEMO_EMAILS = "anna_20@mail.ru hi@dept.example.org user2@site_2.net login@mail bad@@site.ru имя@mail.ru @site.ru name@.ru a-b@site.ru"

# Шаблон допустимых символов для отдельных частей email.fullmatch() проверяет совпадение всей строки с шаблоном.
PART = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class EmailCheck:
    address: str
    reason: str | None


@dataclass(frozen=True)
class EmailResult:
    addresses: tuple[str, ...]
    accepted: tuple[str, ...]
    rejected: tuple[EmailCheck, ...]


# Последовательно проверяем структуру и символы email.
# Возвращаем причину первой ошибки или None, если адрес корректен.
def rejection_reason(address: str) -> str | None:
    if any(character.isspace() for character in address):
        return "Внутри адреса есть пробельный символ."
    separators = address.count("@")
    if separators == 0:
        return "Отсутствует символ @."
    if separators > 1:
        return "Допускается только один символ @."
    local, domain = address.split("@")
    if not local or not domain:
        return "Локальная и доменная части должны быть непустыми."
    if "." not in domain:
        return "После @ нужна точка между частями домена."
    labels = domain.split(".")
    if not all(labels):
        return "Между точками и по краям домена нужны непустые части."
    if not PART.fullmatch(local) or not all(PART.fullmatch(label) for label in labels):
        return "В частях адреса допустимы латинские буквы, цифры и подчёркивание."
    return None


def check_emails(text: str) -> EmailResult:
    addresses = tuple(text.split())
    if not addresses:
        raise InputError("Введите хотя бы один email. Разделяйте адреса пробелами.")

    # Проверяем каждый введённый адрес и сохраняем причину отклонения в объекте EmailCheck.
    checks = tuple(EmailCheck(address, rejection_reason(address)) for address in addresses)

    # filter() оставляет только объекты без ошибок (reason is None). lambda задаёт условие отбора
    accepted = tuple(check.address for check in filter(lambda check: check.reason is None, checks))
    rejected = tuple(check for check in checks if check.reason is not None)

    return EmailResult(addresses, accepted, rejected)
