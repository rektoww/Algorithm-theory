import sqlite3
from pathlib import Path
from .content import Exhibit, Article
from .visitor import Visitor

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "museum.db"

def initialize_database(db_path=None):
    if db_path is None:
        db_path = DB_PATH

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.executescript("""
        CREATE TABLE IF NOT EXISTS contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT,
            author TEXT,
            views INTEGER NOT NULL DEFAULT 0,
            likes INTEGER NOT NULL DEFAULT 0,
            favorites INTEGER NOT NULL DEFAULT 0,
            bookmarks INTEGER NOT NULL DEFAULT 0,
            popularity INTEGER NOT NULL DEFAULT 0
        );
                    
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
            
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id INTEGER NOT NULL,
            content_id INTEGER NOT NULL,    
            action TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (visitor_id) REFERENCES visitors(id),
            FOREIGN KEY (content_id) REFERENCES contents(id)
        );
        
    """)

    return db_path

def save_content(content, db_path=None):
    if not isinstance(content, (Exhibit, Article)):
        raise TypeError("Ожидается Exhibit или Article")

    db_path = initialize_database(db_path)

    if isinstance(content, Exhibit):
        content_type = "exhibit"
        category = content.category
        author = None
        favorites = content.favorites
        bookmarks = 0
    else:
        content_type = "article"
        category = None
        author = content.author
        favorites = 0
        bookmarks = content.bookmarks

    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            INSERT INTO contents (
                id, content_type, title, category, author,
                views, likes, favorites, bookmarks, popularity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                content_type = excluded.content_type,
                category = excluded.category,
                author = excluded.author,
                views = excluded.views,
                likes = excluded.likes,
                favorites = excluded.favorites,
                bookmarks = excluded.bookmarks,
                popularity = excluded.popularity
        """, (
            content.content_id,
            content_type,
            content.title,
            category,
            author,
            content.views,
            content.likes,
            favorites,
            bookmarks,
            content.calculate_popularity()
        ))

def load_contents(db_path=None):
    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            "SELECT * FROM contents ORDER BY id"
        ).fetchall()

    contents = {}

    for row in rows:
        if row["content_type"] == "exhibit":
            content = Exhibit(
                row["id"],
                row["title"],
                row["category"],
                views=row["views"],
                likes=row["likes"],
                favorites=row["favorites"]
            )

        elif row["content_type"] == "article":
            content = Article(
                row["id"],
                row["title"],
                row["author"],
                views=row["views"],
                likes=row["likes"],
                bookmarks=row["bookmarks"]
            )

        else:
            raise ValueError("Неизвестный тип материала в базе")

        contents[content.content_id] = content

    return contents

def create_exhibit(title, category, db_path=None):
    title = title.strip()
    category = category.strip()

    if not title or not category:
        raise ValueError("Название и категория не могут быть пустыми")

    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute("""
            INSERT INTO contents (content_type, title, category)
            VALUES (?, ?, ?)
        """, ("exhibit", title, category))

        new_id = cursor.lastrowid

    return Exhibit(new_id, title, category)


def create_article(title, author, db_path=None):
    title = title.strip()
    author = author.strip()

    if not title or not author:
        raise ValueError("Название и автор не могут быть пустыми")

    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute("""
            INSERT INTO contents (content_type, title, author)
            VALUES (?, ?, ?)
        """, ("article", title, author))

        new_id = cursor.lastrowid

    return Article(new_id, title, author)

def create_visitor(name, db_path=None):
    name = name.strip()

    if not name:
        raise ValueError("Имя посетителя не может быть пустым")

    dp_path = initialize_database(db_path)

    with sqlite3.connect(dp_path) as connection:
        cursor = connection.execute("""
            INSERT INTO visitors (name)
            VALUES (?)
        """, (name,))

        new_id = cursor.lastrowid

    return Visitor(new_id, name)

def save_interaction(visitor, content, action, db_path=None):
    if not isinstance(visitor, Visitor):
        raise TypeError("Ожидается объект Visitor")

    allowed_actions = {
        "view_exhibit": (Exhibit, "views", 1),
        "read_article": (Article, "views", 1),
        "like": ((Exhibit, Article), "likes", 2),
        "favorite": (Exhibit, "favorites", 3),
        "bookmark": (Article, "bookmarks", 3)
    }

    if action not in allowed_actions:
        raise ValueError("Неизвестное действие")

    expected_type, column, points = allowed_actions[action]

    if not isinstance(content, expected_type):
        raise TypeError("Действие не подходит для этого материала")

    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        row = connection.execute(
            "SELECT content_type FROM contents WHERE id = ?",
            (content.content_id,)
        ).fetchone()

        content_type = (
            "exhibit" if isinstance(content, Exhibit)
            else "article"
        )

        if row is None or row[0] != content_type:
            raise ValueError("Материал не найден в базе")

        cursor = connection.execute(
            f"""
            UPDATE contents
            SET {column} = {column} + 1,
                popularity = popularity + ?
            WHERE id = ?
            """,
            (points, content.content_id)
        )

        if cursor.rowcount != 1:
            raise ValueError("Не удалось обновить материал")

        connection.execute("""
            INSERT INTO interactions (
                visitor_id, content_id, action
            )
            VALUES (?, ?, ?)
        """, (
            visitor.visitor_id,
            content.content_id,
            action
        ))

def load_visitors(db_path=None):
    db_path = initialize_database(db_path)

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row

        visitor_rows = connection.execute(
            "SELECT * FROM visitors ORDER BY id"
        ).fetchall()

        interaction_rows = connection.execute(
            "SELECT * FROM interactions ORDER BY id"
        ).fetchall()

    visitors = {}

    for row in visitor_rows:
        visitor = Visitor(row["id"], row["name"])
        visitors[visitor.visitor_id] = visitor

    for row in interaction_rows:
        visitor = visitors[row["visitor_id"]]
        content_id = row["content_id"]
        action = row["action"]

        if action == "view_exhibit":
            visitor.viewed_exhibits.append(content_id)

        elif action == "read_article":
            visitor.read_articles.append(content_id)

        elif action == "like":
            visitor.likes_given += 1

        elif action == "favorite":
            visitor.favorites_added += 1

        elif action == "bookmark":
            visitor.bookmarks_added += 1

        else:
            raise ValueError(f"Неизвестное действие: {action}")

    return visitors