from abc import ABC, abstractmethod

class MuseumContent(ABC):
    #метод инициализации
    def __init__(self, content_id, title, views=0,likes=0):
        self.content_id = content_id
        self.title = title
        self.views = views
        self.likes = likes

    @property
    def content_id(self):
        return self._content_id

    @content_id.setter
    def content_id(self, value):
        if value <= 0:
            raise ValueError("ID должен быть положительным числом")
        self._content_id = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value.strip():
            raise ValueError("Название не может быть пустым")
        self._title = value

    @property
    def views(self):
        return self._views

    @views.setter
    def views(self, value):
        if value < 0:
            raise ValueError("Количество просмотров не может быть отрицательным")
        self._views = value

    @property
    def likes(self):
        return self._likes

    @likes.setter
    def likes(self, value):
        if value < 0:
            raise ValueError("Количество лайков не может быть отрицательным")
        self._likes = value

    def add_view(self):
        self.views += 1

    def add_like(self):
        self.likes += 1

    @abstractmethod
    def calculate_popularity(self):
        pass

    def __str__(self):
        return (f"{self.title}: "
                f"просмотров {self.views}, "
                f"лайков {self.likes}")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"content_id={self.content_id}, "
            f"title={self.title!r}, "
            f"views={self.views}, "
            f"likes={self.likes})"
        )

class Exhibit(MuseumContent):
    def __init__(
        self,
        content_id,
        title,
        category,
        views=0,
        likes=0,
        favorites=0
    ):
        super().__init__(content_id, title, views, likes)
        self.category = category
        self.favorites = favorites

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not value.strip():
            raise ValueError("Категория не может быть пустой")
        self._category = value

    @property
    def favorites(self):
        return self._favorites

    @favorites.setter
    def favorites(self, value):
        if value < 0:
            raise ValueError("Количество добавлений в избранное не может быть отрицательным")
        self._favorites = value

    def add_favorite(self):
        self.favorites += 1

    def calculate_popularity(self):
        return self.views + self.likes * 2 + self.favorites * 3

    def __str__(self):
        return (
            f"Экспонат '{self.title}' "
            f"({self.category}), популярность: {self.calculate_popularity()}"
        )

    def __repr__(self):
        return (
            f'Exhibit(content_id={self.content_id}, '
            f'title={self.title!r}, '
            f'category={self.category!r}, '
            f'views={self.views}, '
            f'likes={self.likes}, '
            f'favorites={self.favorites})'
        )

class Article(MuseumContent):
    def __init__(self,
                 content_id,
                 title,
                 author,
                 views=0,
                 likes=0,
                 bookmarks=0
                 ):
        super().__init__(content_id, title, views, likes)
        self.author = author
        self.bookmarks = bookmarks

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, value):
        if not value.strip():
            raise ValueError('Автор не может быть пустым')
        self._author = value

    @property
    def bookmarks(self):
        return self._bookmarks

    @bookmarks.setter
    def bookmarks(self, value):
        if value < 0:
            raise ValueError('Количество закладок не может быть отрицательным')
        self._bookmarks = value

    def add_bookmark(self):
        self.bookmarks += 1

    def calculate_popularity(self):
        return self.views + self.likes * 2 + self.bookmarks * 3

    def __str__(self):
        return (
            f'Статья «{self.title}», автор {self.author}, '
            f'популярность: {self.calculate_popularity()}'
        )

    def __repr__(self):
        return (
            f'Article(content_id={self.content_id}, '
            f'title={self.title!r}, '
            f'author={self.author!r}, '
            f'views={self.views}, '
            f'likes={self.likes}, '
            f'bookmarks={self.bookmarks})'
        )

