#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Есть словарь координат городов

sites = {
    'Moscow': (550, 370),
    'London': (510, 510),
    'Paris': (480, 480),
}

# Составим словарь словарей расстояний между ними
# расстояние на координатной сетке - ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

distances = {}

sites_list = list(sites.keys())
for i in range(len(sites)):
    distances[sites_list[i]] = {}

for i in range(len(sites)):
    for j in range(i + 1, len(sites)):
        distance = ((sites[sites_list[i]][0] - sites[sites_list[j]][0])**2 + (sites[sites_list[i]][1] - sites[sites_list[j]][1])**2)**0.5
        distances[sites_list[i]][sites_list[j]] = distance
        distances[sites_list[j]][sites_list[i]] = distance

print(distances)
