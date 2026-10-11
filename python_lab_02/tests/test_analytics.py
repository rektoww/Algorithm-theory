import pytest

from virtual_museum.content import Exhibit, Article
from virtual_museum.visitor import Visitor
from virtual_museum.analytics import (
    get_visitor_statistics,
    rank_content,
    most_popular_exhibit,
    most_popular_article
)


def test_visitor_statistics():
    visitor = Visitor(1, "Максим")
    exhibit = Exhibit(1, "Мона Лиза", "Живопись")
    article = Article(2, "История музея", "Иван Иванов")

    visitor.view_exhibit(exhibit)
    visitor.view_exhibit(exhibit)
    visitor.read_article(article)
    visitor.like_content(exhibit)
    visitor.favorite_exhibit(exhibit)
    visitor.bookmark_article(article)

    statistics = get_visitor_statistics(visitor)

    assert statistics["exhibit_views"] == 2
    assert statistics["unique_exhibits"] == 1
    assert statistics["article_reads"] == 1
    assert statistics["unique_articles"] == 1
    assert statistics["likes_given"] == 1
    assert statistics["total_actions"] == 6

def test_rank_content():
    exhibit_1 = Exhibit(
        1, "Мона Лиза", "Живопись",
        views=100, likes=20, favorites=10
    )

    exhibit_2 = Exhibit(
        2, "Звездная ночь", "Живопись",
        views=70, likes=10, favorites=5
    )

    article = Article(
        3, "История музея", "Иван Иванов",
        views=80, likes=15, bookmarks=5
    )

    contents = [exhibit_2, article, exhibit_1]

    ranked = rank_content(contents)

    assert ranked == [exhibit_1, article, exhibit_2]

def test_most_popular_exhibit():
    exhibit_1 = Exhibit(1, "Мона Лиза", "Живопись", views=100)
    exhibit_2 = Exhibit(2, "Звёздная ночь", "Живопись", views=50)
    article = Article(3, "История музея", "Автор", views=200)

    result = most_popular_exhibit([exhibit_1, exhibit_2, article])

    assert result is exhibit_1


def test_most_popular_article():
    article_1 = Article(1, "История музея", "Автор", views=100)
    article_2 = Article(2, "Искусство", "Автор", views=50)
    exhibit = Exhibit(3, "Мона Лиза", "Живопись", views=200)

    result = most_popular_article([article_1, article_2, exhibit])

    assert result is article_1


def test_empty_content():
    assert rank_content([]) == []
    assert most_popular_exhibit([]) is None
    assert most_popular_article([]) is None


def test_invalid_visitor():
    with pytest.raises(TypeError):
        get_visitor_statistics("Максим")