import pytest

from virtual_museum.content import Exhibit, Article
from virtual_museum.visitor import Visitor


def test_visitor_creation():
    visitor = Visitor(1, "Максим")

    assert visitor.visitor_id == 1
    assert visitor.name == "Максим"
    assert visitor.viewed_exhibits == []
    assert visitor.read_articles == []


def test_visitor_views():
    visitor = Visitor(1, "Максим")
    exhibit = Exhibit(1, "Мона Лиза", "Живопись")
    article = Article(2, "История музея", "Иван Иванов")

    visitor.view_exhibit(exhibit)
    visitor.view_exhibit(exhibit)
    visitor.read_article(article)

    assert visitor.viewed_exhibits == [1, 1]
    assert visitor.read_articles == [2]

    assert exhibit.views == 2
    assert article.views == 1

def test_visitor_interactions():
    visitor = Visitor(1, "Максим")
    exhibit = Exhibit(1, "Мона Лиза", "Живопись")
    article = Article(2, "История музея", "Иван Иванов")

    visitor.like_content(exhibit)
    visitor.favorite_exhibit(exhibit)
    visitor.bookmark_article(article)

    assert exhibit.likes == 1
    assert exhibit.favorites == 1
    assert article.bookmarks == 1
    assert visitor.likes_given == 1

def test_invalid_visitor_data():
    with pytest.raises(ValueError):
        Visitor(0, "Максим")

    with pytest.raises(ValueError):
        Visitor(1, "")

def test_invalid_content_type():
    visitor = Visitor(1, "Максим")
    exhibit = Exhibit(1, "Мона Лиза", "Живопись")
    article = Article(2, "История музея", "Иван Иванов")

    with pytest.raises(TypeError):
        visitor.view_exhibit(article)

    with pytest.raises(TypeError):
        visitor.read_article(exhibit)

