import pytest

from virtual_museum.database import (
    create_exhibit,
    create_article,
    load_contents,
    create_visitor,
    load_visitors, save_interaction
)
import sqlite3
from virtual_museum.visitor import Visitor
from virtual_museum.analytics import get_visitor_statistics

def test_create_and_load_contents(tmp_path):
    db_path = tmp_path / "museum_test.db"

    exhibit = create_exhibit(
        "Мона Лиза",
        "Живопись",
        db_path=db_path
    )

    article = create_article(
        "История музея",
        "Иван Иванов",
        db_path=db_path
    )

    assert exhibit.content_id == 1
    assert article.content_id == 2

    contents = load_contents(db_path=db_path)

    assert len(contents) == 2
    assert contents[1].title == "Мона Лиза"
    assert contents[2].title == "История музея"

def test_create_and_load_visitors(tmp_path):
    db_path = tmp_path / "museum_test.db"

    visitor1 = create_visitor("Алексей", db_path)
    visitor2 = create_visitor("Максим", db_path)

    assert visitor1.visitor_id == 1
    assert visitor2.visitor_id == 2

    visitors = load_visitors(db_path)

    assert len(visitors) == 2
    assert visitors[1].name == "Алексей"
    assert visitors[2].name == "Максим"

def test_save_interaction(tmp_path):
    db_path = tmp_path / "museum_test.db"

    exhibit = create_exhibit("Мона Лиза", "Живопись", db_path)
    visitor = create_visitor("Алексей", db_path)

    save_interaction(visitor, exhibit, "like", db_path)

    contents = load_contents(db_path)
    visitors = load_visitors(db_path)

    restored_exhibit = contents[exhibit.content_id]
    restored_visitor = visitors[visitor.visitor_id]

    assert restored_exhibit.likes == 1
    assert restored_exhibit.calculate_popularity() == 2

    assert restored_visitor.likes_given == 1

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT visitor_id, content_id, action FROM interactions"
        ).fetchall()

    assert len(rows) == 1
    assert rows[0] == (visitor.visitor_id, exhibit.content_id, "like")

def test_foreign_key_constraint(tmp_path):
    db_path = tmp_path / "museum_test.db"

    exhibit = create_exhibit("Мона Лиза", "Живопись", db_path)

    fake_visitor = Visitor(999, "Неизвестный")

    with pytest.raises(sqlite3.IntegrityError):
        save_interaction(fake_visitor, exhibit, "like", db_path)

    contents = load_contents(db_path)
    restored_exhibit = contents[exhibit.content_id]

    assert restored_exhibit.likes == 0
    assert restored_exhibit.calculate_popularity() == 0

def test_multiple_interactions(tmp_path):
    db_path = tmp_path / "museum_test.db"

    exhibit = create_exhibit("Мона Лиза", "Живопись", db_path)
    article = create_article("История музея", "Иван Иванов", db_path)
    visitor = create_visitor("Алексей", db_path)

    actions = [
        ("view_exhibit", exhibit),
        ("like", exhibit),
        ("favorite", exhibit),
        ("read_article", article),
        ("bookmark", article)
    ]

    for action, content in actions:
        save_interaction(visitor, content, action, db_path)

    contents = load_contents(db_path)
    visitors = load_visitors(db_path)

    restored_exhibit = contents[exhibit.content_id]
    restored_article = contents[article.content_id]
    restored_visitor = visitors[visitor.visitor_id]

    assert restored_exhibit.calculate_popularity() == 6
    assert restored_article.calculate_popularity() == 4

    statistics = get_visitor_statistics(restored_visitor)

    assert statistics["exhibit_views"] == 1
    assert statistics["article_reads"] == 1
    assert statistics["likes_given"] == 1
    assert statistics["favorites_given"] == 1
    assert statistics["bookmarks_added"] == 1
    assert statistics["total_actions"] == 5

    contents_again = load_contents(db_path)
    visitors_again = load_visitors(db_path)

    assert contents_again[exhibit.content_id].calculate_popularity() == 6

    statistics_again = get_visitor_statistics(
        visitors_again[visitor.visitor_id]
    )

    assert statistics_again["total_actions"] == 5