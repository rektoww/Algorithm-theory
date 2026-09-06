#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Есть список животных в зоопарке
zoo = ['lion', 'kangaroo', 'elephant', 'monkey']

# Посадите медведя (bear) между львом и кенгуру
# и выведите список на консоль
# TODO здесь ваш код

# Добавьте птиц из списка birds в последние клетки зоопарка
birds = ['rooster', 'ostrich', 'lark']
# и выведите список на консоль
# TODO здесь ваш код

# Уберите слона (elephant) из зоопарка
# и выведите список на консоль
# TODO здесь ваш код

# Выведите на консоль в какой клетке сидит лев (lion) и жаворонок (lark).
# Номера при выводе должны быть 1-индексированными (первая клетка - номер 1).
# TODO здесь ваш код

def update_zoo(zoo, birds):
    result = zoo.copy()

    result.insert(1, 'bear')
    result += birds
    result.remove('elephant')

    return result


def get_cage_number(zoo, animal):
    return zoo.index(animal) + 1


def run():
    updated_zoo = zoo.copy()

    updated_zoo.insert(1, 'bear')
    print(updated_zoo)

    updated_zoo += birds
    print(updated_zoo)

    updated_zoo.remove('elephant')
    print(updated_zoo)

    print(f"Лев (lion) живёт в клетке {get_cage_number(updated_zoo, 'lion')}")
    print(f"Жаворонок (lark) живёт в клетке {get_cage_number(updated_zoo, 'lark')}")


if __name__ == '__main__':
    run()