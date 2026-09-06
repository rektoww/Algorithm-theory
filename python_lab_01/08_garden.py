#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# В саду сорвали цветы
garden = ('ромашка', 'роза', 'одуванчик', 'ромашка', 'гладиолус', 'подсолнух', 'роза', )

# На лугу сорвали цветы
meadow = ('клевер', 'одуванчик', 'ромашка', 'клевер', 'мак', 'одуванчик', 'ромашка', )

# Создайте множество цветов, произрастающих в саду и на лугу
# garden_set =
# meadow_set =
# TODO здесь ваш код

# Выведите на консоль все виды цветов
# TODO здесь ваш код


# Выведите на консоль те, которые растут и там и там
# TODO здесь ваш код


# Выведите на консоль те, которые растут в саду, но не растут на лугу
# TODO здесь ваш код

# Выведите на консоль те, которые растут на лугу, но не растут в саду
# TODO здесь ваш код

def analyze_flowers(garden, meadow):
    garden_set = set(garden)
    meadow_set = set(meadow)

    return {
        'all': garden_set | meadow_set,
        'garden_and_meadow': garden_set & meadow_set,
        'garden_only': garden_set - meadow_set,
        'meadow_only': meadow_set - garden_set,
    }


def run():
    result = analyze_flowers(garden, meadow)

    print(result['all'])
    print(result['garden_and_meadow'])
    print(result['garden_only'])
    print(result['meadow_only'])


if __name__ == '__main__':
    run()