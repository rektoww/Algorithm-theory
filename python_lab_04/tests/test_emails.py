import pytest

from lab04.core.emails import DEMO_EMAILS, check_emails, rejection_reason
from lab04.core.errors import InputError


@pytest.mark.parametrize("address", ["mail@site.ru", "I_2@DEPT.sub3.NET", "_@_._", "0@1.2"])
def test_accepts_educational_format(address):
    assert rejection_reason(address) is None


@pytest.mark.parametrize(("address", "expected"), [
    ("имя@site.ru", "латинские"), ("name@сайт.ru", "латинские"), ("na-me@site.ru", "латинские"),
    ("f.o@site.ru", "латинские"), ("site.ru", "Отсутствует"), ("name@site", "точка"),
    ("@site.ru", "непустыми"), ("name@", "непустыми"), ("name@.ru", "непустые"),
    ("name@site..ru", "непустые"), ("name@site.ru.", "непустые"), ("name@@site.ru", "один"),
    ("na me@site.ru", "пробельный"), ("name@site. ru", "пробельный"),
])
def test_rejected_reasons(address, expected):
    assert expected in rejection_reason(address)


@pytest.mark.parametrize("text", ["", "   \t "])
def test_empty_input(text):
    with pytest.raises(InputError, match="хотя бы один"):
        check_emails(text)


def test_order_whitespace_and_repetitions():
    result = check_emails("  z@site.ru  broken\ta@site.ru bad@site  z@site.ru  ")
    assert result.addresses == ("z@site.ru", "broken", "a@site.ru", "bad@site", "z@site.ru")
    assert result.accepted == ("z@site.ru", "a@site.ru", "z@site.ru")
    assert [item.address for item in result.rejected] == ["broken", "bad@site"]


def test_demo_has_both_classes():
    result = check_emails(DEMO_EMAILS)
    assert len(result.accepted) == 3
    assert len(result.rejected) == 6
