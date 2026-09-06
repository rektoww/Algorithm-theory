from importlib import import_module


task_modules = [
    '00_distance',
    '01_circle',
    '02_operations',
    '03_favorite_movies',
    '04_my_family',
    '05_zoo',
    '06_songs_list',
    '07_secret',
    '08_garden',
    '09_shopping',
    '10_store',
]


def main():
    for module_name in task_modules:
        module = import_module(f'python_lab_01.{module_name}')
        module.run()
        print()


if __name__ == '__main__':
    main()