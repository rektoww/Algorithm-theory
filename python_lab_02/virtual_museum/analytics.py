from .content import MuseumContent, Exhibit, Article
from .visitor import Visitor

def get_visitor_statistics(visitor):
    if not isinstance(visitor, Visitor):
        raise TypeError("Ожидается объект Visitor")

    exhibit_views = len(visitor.viewed_exhibits)
    article_reads = len(visitor.read_articles)

    total_actions = (
        exhibit_views
        + article_reads
        + visitor.likes_given
        + visitor.favorites_added
        + visitor.bookmarks_added
    )

    return {
        "visitor_id": visitor.visitor_id,
        "name": visitor.name,
        "exhibit_views": exhibit_views,
        "unique_exhibits": len(set(visitor.viewed_exhibits)),
        "article_reads": article_reads,
        "unique_articles": len(set(visitor.read_articles)),
        "likes_given": visitor.likes_given,
        "favorites_given": visitor.favorites_added,
        "bookmarks_added": visitor.bookmarks_added,
        "total_actions": total_actions
    }

def rank_content(contents):
    return sorted(
        contents,
        key=lambda content: content.calculate_popularity(),
        reverse=True
    )

def most_popular_exhibit(contents):
    exhibits = [
        content for content in contents
        if isinstance(content, Exhibit)
    ]

    if not exhibits:
        return None

    return max(
        exhibits,
        key=lambda content: content.calculate_popularity()
    )

def most_popular_article(contents):
    articles = [
        content for content in contents
        if isinstance(content, Article)
    ]

    if not articles:
        return None

    return max(
        articles,
        key=lambda content: content.calculate_popularity()
    )