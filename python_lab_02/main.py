import sqlite3
from virtual_museum.content import Exhibit, Article
from virtual_museum.visitor import Visitor
from virtual_museum.analytics import (
    get_visitor_statistics,
    rank_content,
    most_popular_article,
    most_popular_exhibit
)
from virtual_museum.report import export_report, export_excel
from virtual_museum.database import (
    create_exhibit,
    create_article,
    create_visitor,
    load_contents,
    load_visitors,
    save_interaction
)


def read_positive_int(message):
    while True:
        try:
            value = int(input(message))

            if value <= 0:
                print("Введите положительное число.")
                continue

            return value

        except ValueError:
            print("Ошибка: необходимо ввести целое число")


def add_exhibit(contents):
    print("\n--- Новый экспонат ---")

    title = input("Название: ")
    category = input("Категория: ")

    exhibit = create_exhibit(title, category)
    contents[exhibit.content_id] = exhibit

    print(f"Экспонат успешно добавлен (ID: {exhibit.content_id})")


def add_article(contents):
    print("\n-- Новая статья ---")

    title = input("Название: ")
    author = input("Автор: ")

    article = create_article(title, author)
    contents[article.content_id] = article

    print(f"Статья успешно добавлена (ID: {article.content_id})")


def add_visitor(visitors):
    print("\n--- Регистрация посетителя ---")

    name = input("Имя: ")

    visitor = create_visitor(name)
    visitors[visitor.visitor_id] = visitor

    print(f"Посетитель зарегистрирован (ID: {visitor.visitor_id})")


def perform_action(contents, visitors):
    if not contents or not visitors:
        print("Сначала добавьте материалы и посетителей")
        return

    print("\n--- Действие посетителя ---")

    print("Посетители:")
    for visitor in visitors.values():
        print(f"{visitor.visitor_id}: {visitor.name}")

    visitor_id = read_positive_int("ID посетителя: ")
    visitor = visitors.get(visitor_id)

    if visitor is None:
        print("Посетитель не найден")
        return

    print("\nМатериалы:")
    for content in contents.values():
        print(f"{content.content_id}: {content.title}")

    content_id = read_positive_int("ID материала: ")
    content = contents.get(content_id)

    if content is None:
        print("Материал не найден")
        return

    print("\nВыберите действие:")

    if isinstance(content, Exhibit):
        print("1. Посмотреть экспонат")
        print("2. Поставить лайк")
        print("3. Добавить в избранное")
    elif isinstance(content, Article):
        print("1. Прочитать статью")
        print("2. Поставить лайк")
        print("3. Добавить в закладки")

    action = input("Действие: ")

    if action == "1":
        if isinstance(content, Exhibit):
            action_name = "view_exhibit"
        else:
            action_name = "read_article"
    elif action == "2":
        action_name = "like"
    elif action == "3":
        if isinstance(content, Exhibit):
            action_name = "favorite"
        else:
            action_name = "bookmark"

    else:
        print("Неизвестное действие")
        return

    save_interaction(visitor, content, action_name)

    if action_name == "view_exhibit":
        visitor.view_exhibit(content)

    elif action_name == "read_article":
        visitor.read_article(content)

    elif action_name == "like":
        visitor.like_content(content)

    elif action_name == "favorite":
        visitor.favorite_exhibit(content)

    elif action_name == "bookmark":
        visitor.bookmark_article(content)

    print("Действие успешно выполнено")

def show_catalog(contents):
    if not contents:
        print("Каталог пока пуст")
        return

    print("\n--- Рейтинг материалов ---")

    for content in rank_content(list(contents.values())):
        print(
            f"ID: {content.content_id} | "
            f"{content.title} | "
            f"Популярность: {content.calculate_popularity()}"
        )


def show_visitor_statistics(visitors):
    if not visitors:
        print("Посетители пока не зарегистрированы")
        return

    print("\n--- Статистика посетителя ---")

    for visitor in visitors.values():
        print(f"{visitor.visitor_id}: {visitor.name}")

    visitor_id = read_positive_int("ID посетителя: ")
    visitor = visitors.get(visitor_id)

    if visitor is None:
        print("Посетитель не найден")
        return

    statistics = get_visitor_statistics(visitor)

    for key, value in statistics.items():
        print(f"{key}: {value}")


def show_popular_content(contents):
    if not contents:
        print("Каталог пока пуст")
        return

    materials = list(contents.values())

    exhibit = most_popular_exhibit(materials)
    article = most_popular_article(materials)

    print("\n--- Самые популярные материалы ---")

    if exhibit is not None:
        print(f"Экспонат: {exhibit}")
    else:
        print("Экспонатов пока нет")

    if article is not None:
        print(f"Статья: {article}")
    else:
        print("Статей пока нет")


def main():
    contents = load_contents()
    visitors = load_visitors()

    while True:
        print("\n========== ВИРТУАЛЬНЫЙ МУЗЕЙ ==========")
        print("1. Добавить экспонат")
        print("2. Добавить статью")
        print("3. Зарегистрировать посетителя")
        print("4. Выполнить действие посетителя")
        print("5. Посмотреть каталог и рейтинг")
        print("6. Статистика посетителя")
        print("7. Самые популярные материалы")
        print("8. Сохранить отчёт в Word")
        print("9. Сохранить отчёт в Excel")
        print("0. Выход")

        choice = input("\nВыберите действие: ")

        try:
            if choice == "1":
                add_exhibit(contents)

            elif choice == "2":
                add_article(contents)

            elif choice == "3":
                add_visitor(visitors)

            elif choice == "4":
                perform_action(contents, visitors)

            elif choice == "5":
                show_catalog(contents)

            elif choice == "6":
                show_visitor_statistics(visitors)

            elif choice == "7":
                show_popular_content(contents)

            elif choice == "8":
                file_path = export_report(contents, visitors)
                print(f"Отчёт успешно сохранён: {file_path}")

            elif choice == "9":
                file_path = export_excel(contents, visitors)
                print(f"Excel-отчет успешно сохранен: {file_path}")

            elif choice == "0":
                print("Завершение работы")
                break

            else:
                print("Неизвестная команда")

        except (ValueError, TypeError, OSError, sqlite3.Error) as error:
            print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()
