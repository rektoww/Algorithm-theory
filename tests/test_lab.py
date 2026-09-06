from importlib import import_module

import pytest

distance = import_module('python_lab_01.00_distance')
circle = import_module('python_lab_01.01_circle')
operations = import_module('python_lab_01.02_operations')
movies = import_module('python_lab_01.03_favorite_movies')
family = import_module('python_lab_01.04_my_family')
zoo = import_module('python_lab_01.05_zoo')
songs = import_module('python_lab_01.06_songs_list')
secret = import_module('python_lab_01.07_secret')
garden = import_module('python_lab_01.08_garden')
shopping = import_module('python_lab_01.09_shopping')
store = import_module('python_lab_01.10_store')

def test_calculate_distances():
    sites = {
        'A': (0, 0),
        'B': (3, 4),
    }

    result = distance.calculate_distances(sites)

    assert result['A']['B'] == 5
    assert result['B']['A'] == 5

def test_calculate_circle_area():
    result = circle.calculate_circle_area(42)

    assert result == pytest.approx(5541.7693464)


def test_point_inside_circle():
    assert circle.is_point_inside_circle((23, 34), 42) is True


def test_point_outside_circle():
    assert circle.is_point_inside_circle((30, 30), 42) is False


def test_point_on_circle_border():
    assert circle.is_point_inside_circle((42, 0), 42) is True

def test_operations_example():
    assert operations.calculate_example() == 9


def test_operations_result():
    assert operations.calculate_result() == 25

def test_selected_movies():
    result = movies.get_selected_movies(movies.my_favorite_movies)

    assert result == (
        'Терминатор',
        'Назад в будущее',
        'Пятый элемент',
        'Чужие',
    )

def test_family_height():
    _, family_height = family.create_family_data()

    assert family.get_father_height(family_height) == 184
    assert family.calculate_family_height(family_height) == 891

def test_update_zoo():
    result = zoo.update_zoo(
        ['lion', 'kangaroo', 'elephant', 'monkey'],
        ['rooster', 'ostrich', 'lark']
    )

    assert result == [
        'lion',
        'bear',
        'kangaroo',
        'monkey',
        'rooster',
        'ostrich',
        'lark',
    ]


def test_cage_numbers():
    result = [
        'lion',
        'bear',
        'kangaroo',
        'monkey',
        'rooster',
        'ostrich',
        'lark',
    ]

    assert zoo.get_cage_number(result, 'lion') == 1
    assert zoo.get_cage_number(result, 'lark') == 7

def test_list_songs_duration():
    result = songs.calculate_list_songs_duration(
        songs.violator_songs_list
    )

    assert result == pytest.approx(14.93)


def test_dict_songs_duration():
    result = songs.calculate_dict_songs_duration(
        songs.violator_songs_dict
    )

    assert result == pytest.approx(13.49)

def test_decrypt_message():
    result = secret.decrypt_message(secret.secret_message)

    assert result == 'в бане веник дороже денег'

def test_analyze_flowers():
    result = garden.analyze_flowers(
        ('ромашка', 'роза', 'одуванчик'),
        ('клевер', 'одуванчик', 'ромашка')
    )

    assert result['all'] == {
        'ромашка',
        'роза',
        'одуванчик',
        'клевер',
    }

    assert result['garden_and_meadow'] == {
        'ромашка',
        'одуванчик',
    }

    assert result['garden_only'] == {'роза'}
    assert result['meadow_only'] == {'клевер'}

def test_sweets():
    result = shopping.get_sweets()

    assert result['печенье'] == [
        {'shop': 'пятерочка', 'price': 9.99},
        {'shop': 'ашан', 'price': 10.99},
    ]

    assert result['конфеты'] == [
        {'shop': 'магнит', 'price': 30.99},
        {'shop': 'пятерочка', 'price': 32.99},
    ]

def test_calculate_store():
    result = store.calculate_store(store.goods, store.store)

    assert result['Лампа'] == {
        'quantity': 27,
        'price': 1134,
    }

    assert result['Стол'] == {
        'quantity': 54,
        'price': 27860,
    }

    assert result['Диван'] == {
        'quantity': 3,
        'price': 3550,
    }

    assert result['Стул'] == {
        'quantity': 105,
        'price': 10311,
    }