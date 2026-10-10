from .content import MuseumContent, Exhibit, Article

class Visitor:
    def __init__(self, visitor_id, name):
        self.visitor_id = visitor_id
        self.name = name

        self.viewed_exhibits = []
        self.read_articles = []

        self.likes_given = 0
        self.favorites_added = 0
        self.bookmarks_added = 0

    @property
    def visitor_id(self):
        return self._visitor_id

    @visitor_id.setter
    def visitor_id(self, value):
        if value <= 0:
            raise ValueError("ID посетителя должен быть положительным числом")
        self._visitor_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value.strip():
            raise ValueError("Имя посетителя не может быть пустым")
        self._name = value

    def view_exhibit(self, exhibit):
        if not isinstance(exhibit, Exhibit):
            raise TypeError("Ожидается объект Exhibit")

        exhibit.add_view()
        self.viewed_exhibits.append(exhibit.content_id)

    def read_article(self, article):
        if not isinstance(article, Article):
            raise TypeError("Ожидается объект Article")

        article.add_view()
        self.read_articles.append(article.content_id)

    def like_content(self, content):
        if not isinstance(content, MuseumContent):
            raise TypeError("Ожидается музейный объект MuseumContent")

        content.add_like()
        self.likes_given += 1

    def favorite_exhibit(self, exhibit):
        if not isinstance(exhibit, Exhibit):
            raise TypeError("Ожидается объект Exhibit")

        exhibit.add_favorite()
        self.favorites_added += 1

    def bookmark_article(self, article):
        if not isinstance(article, Article):
            raise TypeError("Ожидается объект Article")

        article.add_bookmark()
        self.bookmarks_added += 1

    def __str__(self) -> str:
        return f"Посетитель {self.name}"

    def __repr__(self) -> str:
        return (
            f"Visitor("
            f"visitor_id={self.visitor_id}, "
            f"name={self.name!r})"
        )

