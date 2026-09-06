# Algorithm-theory
Репозиторий для выполнения работ по дисциплине "Теория алгоритмов", 3 курс.

# Лабораторная работа № 1 — Теория алгоритмов

## Описание

Лабораторная работа посвящена знакомству с языком Python, базовыми структурами данных, организацией проекта с Git, импортированием модулей и автоматизированным тестированием.

В проекте выполнены 11 заданий, реализован верхнеуровневый модуль `main.py`, а функциональность покрыта тестами `pytest`.

## Структура проекта

```text
LR1/
├── main.py
├── README.md
├── requirements.txt
├── python_lab_01/
│   ├── __init__.py
│   ├── 00_distance.py
│   ├── 01_circle.py
│   ├── 02_operations.py
│   ├── 03_favorite_movies.py
│   ├── 04_my_family.py
│   ├── 05_zoo.py
│   ├── 06_songs_list.py
│   ├── 07_secret.py
│   ├── 08_garden.py
│   ├── 09_shopping.py
│   └── 10_store.py
└── tests/
    └── test_lab.py
```

## Выполненные задания

| Файл | Содержание |
|---|---|
| `00_distance.py` | Расчёт расстояний между городами и формирование словаря словарей |
| `01_circle.py` | Площадь круга и проверка положения точек |
| `02_operations.py` | Арифметическое выражение с результатом 25 |
| `03_favorite_movies.py` | Индексация и срезы строк |
| `04_my_family.py` | Работа со списками и вычисление общего роста |
| `05_zoo.py` | Добавление, удаление и поиск элементов списка |
| `06_songs_list.py` | Работа со списком списков и словарём |
| `07_secret.py` | Расшифровка сообщения с помощью срезов |
| `08_garden.py` | Операции над множествами |
| `09_shopping.py` | Вложенные словари и минимальные цены |
| `10_store.py` | Расчёт количества и общей стоимости товаров |

## Верхнеуровневый модуль

Исполняемая логика каждого задания помещена в функции. Для демонстрационного запуска модуль содержит функцию `run()` и конструкцию:

```python
if __name__ == '__main__':
    run()
```

Файлы заданий начинаются с цифр, поэтому в `main.py` для их импортирования используется `import_module()`:

```python
from importlib import import_module

module = import_module('python_lab_01.00_distance')
module.run()
```

Запуск всех заданий:

```bash
python main.py
```

## Установка зависимостей

Рекомендуется использовать виртуальное окружение.

```bash
python -m venv .venv
```

После активации окружения установить зависимости:

```bash
python -m pip install -r requirements.txt
```

## Тестирование

Тесты реализованы с использованием `pytest` и находятся в `tests/test_lab.py`.

Запуск:

```bash
python -m pytest -v
```

Результат проверки проекта: **17 passed**.

## Git

Основные команды, использованные в работе:

```bash
git status
git switch -c LR1
git add .
git commit -m "Complete laboratory work 1"
git push -u origin LR1
```

После установки upstream для следующих отправок достаточно:

```bash
git push
```

## Использованные материалы

1. [Python Tutorial](https://docs.python.org/3/tutorial/)
2. [Markdown — Дока](https://doka.guide/tools/markdown/)
3. [pytest documentation](https://docs.pytest.org/en/latest/)
4. [Git documentation](https://git-scm.com/docs)
5. [Пример отчёта в Markdown](https://github.com/still-coding/report_demo)
