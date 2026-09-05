#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Создайте списки:

# моя семья (минимум 3 элемента, есть еще дедушки и бабушки, если что)
my_family = []

# список списков приблизительного роста членов вашей семьи
my_family_height = [
    # ['имя', рост],
]

# Выведите на консоль рост отца в формате
#   Рост отца - ХХ см

# Выведите на консоль общий рост вашей семьи как сумму ростов всех членов
#   Общий рост моей семьи - ХХ см

# TODO здесь ваш код

my_family.append('Папа')
my_family.append('Мама')
my_family.append('Старший брат')
my_family.append('Старшая сестра')
my_family.append('Я')

my_family_height.append([my_family[0], 184])
my_family_height.append([my_family[1], 170])
my_family_height.append([my_family[2], 185])
my_family_height.append([my_family[3], 172])
my_family_height.append([my_family[4], 180])

summary_family_height = sum(member[1] for member in my_family_height)

print(f"Рост отца - {my_family_height[0][1]} см")
print(f"Общий рост моей семьи - {summary_family_height} см")

