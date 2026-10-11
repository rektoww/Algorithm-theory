import pytest

from virtual_museum.content import MuseumContent, Exhibit, Article

def test_exhibit_popularity():
    exhibit = Exhibit(
        1, "Мона Лиза", "Живопись", views=100, likes=20, favorites=10
    )

    assert exhibit.calculate_popularity() == 170

def test_article_popularity():
    article = Article(
        2, "История музея", "Иван Иванов", views=80, likes=15, bookmarks=5
    )

    assert article.calculate_popularity() == 125

def test_add_view_and_like():
    exhibit = Exhibit(1, "Мона Лиза", "Живопись")

    exhibit.add_view()
    exhibit.add_like()
    exhibit.add_favorite()

    assert exhibit.views == 1
    assert exhibit.likes == 1
    assert exhibit.favorites == 1

def test_invalid_values():
    exhibit = Exhibit(1, "Мона Лиза", "Живопись")

    with pytest.raises(ValueError):
        exhibit.views = -5

    with pytest.raises(ValueError):
        exhibit.likes = -1

def test_abstract_class():
    with pytest.raises(TypeError):
        MuseumContent(1, "Название")