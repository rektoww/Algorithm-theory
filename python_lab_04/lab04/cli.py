import argparse
import multiprocessing
import sys
from itertools import islice

from .core.benchmark import DEFAULT_CPU_COUNT, DEFAULT_CPU_ROUNDS, DEFAULT_REPEATS, compare
from .core.emails import DEMO_EMAILS, check_emails
from .core.errors import LabError, check_range, parse_integer
from .core.generation import Mode, run_notes
from .core.multiples import multiples_of_three
from .core.notes import DEFAULT_BATCH_SIZE, DEFAULT_COUNT, MAX_ROUNDS, NOTES, NotesConfig
from .core.parallel import default_workers, max_workers

# Описываем доступные CLI-команды и их параметры.
# argparse разбирает аргументы запуска и формирует объект Namespace.
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Лабораторная работа № 4, вариант 20.")
    commands = parser.add_subparsers(dest="command", required=True)
    notes = commands.add_parser("notes", help="сгенерировать ноты и подсчитать частоты")
    multiples = commands.add_parser("multiples", help="получить числа, кратные трём")
    emails = commands.add_parser("emails", help="отфильтровать email-адреса")
    benchmark = commands.add_parser("benchmark", help="измерить производительность генерации")

    for command in (notes, benchmark):
        command.add_argument("--count", help="количество нот")
        command.add_argument("--seed", help="фиксированное целое зерно")
        command.add_argument("--workers", default=str(default_workers()), help="число процессов в пуле")
        command.add_argument("--batch-size", default=str(DEFAULT_BATCH_SIZE), help="нот в пакете")
    notes.add_argument("--mode", choices=list(Mode), default=Mode.SEQUENTIAL.value)
    multiples.add_argument("--start", default="-100", help="начальное значение a")
    multiples.add_argument("--count", default="20", help="количество выводимых чисел")
    source = emails.add_mutually_exclusive_group(required=True)
    source.add_argument("text", nargs="?", help="строка адресов в кавычках")
    source.add_argument("--demo", action="store_true", help="проверить демонстрационный набор")
    benchmark.add_argument("--scenario", choices=("standard", "cpu"), default="standard")
    benchmark.add_argument("--mode", choices=("compare", *Mode), default="compare")
    benchmark.add_argument("--rounds", help="итерации SHA-256 на ноту для сценария cpu")
    benchmark.add_argument("--repeats", default=str(DEFAULT_REPEATS), help="повторы после прогрева")
    return parser


# Выполняет выбранную CLI-команду.
# Использует те же функции core, что и графический интерфейс, но результаты выводит через print().
def run(args: argparse.Namespace) -> None:
    if args.command == "multiples":
        start = parse_integer(args.start, "Начальное значение a")
        count = parse_integer(args.count, "Количество чисел")
        check_range(count, 1, 10_000, "Количество чисел")
        print(" ".join(map(str, islice(multiples_of_three(start), count))))
        return
    if args.command == "emails":
        result = check_emails(DEMO_EMAILS if args.demo else args.text)
        print("Исходные адреса —", ", ".join(result.addresses))
        print("Принятые —", ", ".join(result.accepted) or "нет")
        for item in result.rejected:
            print(f"Отклонён {item.address} — {item.reason}")
        print(f"Всего {len(result.addresses)} · приняты {len(result.accepted)} · отклонены {len(result.rejected)}")
        return

    # Для нагрузочного сценария cpu включаем SHA-256
    # и используем отдельные значения по умолчанию.
    # Для обычного сценария rounds остаётся равным 0.
    cpu = args.command == "benchmark" and args.scenario == "cpu"
    default_count = DEFAULT_CPU_COUNT if cpu else DEFAULT_COUNT
    rounds = 0
    if cpu:
        rounds = parse_integer(args.rounds, "Итерации SHA-256") if args.rounds is not None else DEFAULT_CPU_ROUNDS
        check_range(rounds, 1, MAX_ROUNDS, "Итерации SHA-256")
    elif args.command == "benchmark" and args.rounds is not None:
        raise LabError("Параметр --rounds используется со сценарием --scenario cpu.")
    config = NotesConfig(
        parse_integer(args.count, "Количество нот") if args.count is not None else default_count,
        parse_integer(args.seed, "Seed") if args.seed is not None else None,
        parse_integer(args.batch_size, "Размер пакета"),
        rounds,
    )
    workers = parse_integer(args.workers, "Количество процессов")
    check_range(workers, 1, max_workers(), "Количество процессов")
    if args.command == "notes":
        output = run_notes(config, Mode(args.mode), workers)
        summary = output.result.summary
        print("Первые ноты —", " · ".join(summary.preview))
        for note, frequency in zip(NOTES, summary.frequencies, strict=True):
            print(f"{note:>4}  {frequency}")
        print(f"Всего {summary.count} · сумма частот {sum(summary.frequencies)} · seed {output.seed}")
        print(f"Время {output.seconds:.6f} с · процессов с пакетами {len(output.result.process_ids)} из {output.pool_workers}")
        return

    repeats = parse_integer(args.repeats, "Количество повторов")
    mode = None if args.mode == "compare" else Mode(args.mode)
    result = compare(config, workers, repeats, mode)
    print(f"Нот {config.count} · пакет {config.batch_size} · итераций SHA-256 на ноту {config.rounds} · seed {result.seed}")
    for measurement in (result.sequential, result.parallel):
        if measurement is not None:
            print(f"{measurement.mode.label} — медиана {measurement.median_seconds:.6f} с, процессов с пакетами {measurement.process_count}")
            print("  Замеры в секундах —", ", ".join(f"{sample:.6f}" for sample in measurement.samples))
    if result.parallel is not None:
        print(f"Подготовка пула ({result.pool_workers} процессов) — {result.pool_setup_seconds:.6f} с, отдельно от замеров")
    if result.speedup is not None:
        print(f"Ускорение {result.speedup:.3f}× · экономия времени {result.time_saved_percent:+.2f} %")
        print(result.explanation)

# Разбираем аргументы запуска, выполняем команду и возвращаем код завершения для терминала или Docker.
def main() -> int:
    args = build_parser().parse_args()
    try:
        run(args)
    except LabError as exc:
        print(f"Ошибка. {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Операция прервана.", file=sys.stderr)
        return 130
    except ValueError as exc:
        print(f"Ошибка при выводе результата. Проверьте входные значения. {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
