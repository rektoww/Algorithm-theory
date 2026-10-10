from virtual_museum.content import Exhibit, Article
from virtual_museum.visitor import Visitor
from virtual_museum.analytics import (
    get_visitor_statistics,
    rank_content,
    most_popular_exhibit,
    most_popular_article
)


def main():
    exhibit_1 = Exhibit(
        1, "Мона Лиза", "Живопись",
        views=100, likes=20, favorites=10
    )

    exhibit_2 = Exhibit(
        2, "Звёздная ночь", "Живопись",
        views=70, likes=10, favorites=5
    )

    article = Article(
        3, "История музея", "Иван Иванов",
        views=80, likes=15, bookmarks=5
    )

    visitor = Visitor(1, "Максим")

    visitor.view_exhibit(exhibit_1)
    visitor.view_exhibit(exhibit_1)
    visitor.read_article(article)
    visitor.like_content(exhibit_1)
    visitor.favorite_exhibit(exhibit_1)
    visitor.bookmark_article(article)

    contents = [exhibit_1, exhibit_2, article]

    print("Статистика посетителя:")
    print(get_visitor_statistics(visitor))

    print("\nРейтинг контента:")
    for content in rank_content(contents):
        print(content.title, content.calculate_popularity())

    print("\nСамый популярный экспонат:")
    print(most_popular_exhibit(contents))

    print("\nСамая популярная статья:")
    print(most_popular_article(contents))


if __name__ == "__main__":
    main()