"""Проверка вывода решения задачи «Миллиард строк».

Использование:
    uv run main.py data/measurements_1k.txt | python data/check.py data/measurements_1k.out
    python data/check.py data/measurements_1k.out my_output.txt

Ожидаемый формат: одна строка на станцию, ``<станция>;<min>;<mean>;<max>``,
станции отсортированы по названию. min и max должны совпадать точно,
mean допускает расхождение в 0.1 (на случай разницы в округлении).
"""

import sys


def parse(text: str) -> dict[str, tuple[float, float, float]]:
    result = {}
    names = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line:
            continue
        parts = line.rsplit(";", 3)
        if len(parts) != 4:
            raise ValueError(f"строка {number}: ожидалось <станция>;<min>;<mean>;<max>, получено {line!r}")
        name, *values = parts
        try:
            lo, mean, hi = (float(v) for v in values)
        except ValueError:
            raise ValueError(f"строка {number}: не удалось разобрать числа в {line!r}") from None
        if name in result:
            raise ValueError(f"строка {number}: станция {name!r} выведена повторно")
        result[name] = (lo, mean, hi)
        names.append(name)
    if names != sorted(names):
        raise ValueError("станции не отсортированы по названию")
    return result


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print(__doc__, file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        expected_text = f.read()
    if len(sys.argv) == 3:
        with open(sys.argv[2], encoding="utf-8") as f:
            actual_text = f.read()
    else:
        actual_text = sys.stdin.read()

    expected = parse(expected_text)
    try:
        actual = parse(actual_text)
    except ValueError as e:
        print(f"FAIL: неверный формат: {e}")
        return 1

    errors = []
    for name in expected.keys() - actual.keys():
        errors.append(f"нет станции {name!r}")
    for name in actual.keys() - expected.keys():
        errors.append(f"лишняя станция {name!r}")
    for name in expected.keys() & actual.keys():
        (elo, emean, ehi), (alo, amean, ahi) = expected[name], actual[name]
        if elo != alo or ehi != ahi or abs(emean - amean) > 0.1 + 1e-9:
            errors.append(
                f"{name}: ожидалось {elo};{emean};{ehi}, получено {alo};{amean};{ahi}"
            )

    if errors:
        print(f"FAIL: {len(errors)} ошибок")
        for e in sorted(errors)[:20]:
            print("  " + e)
        return 1
    exact = actual_text.strip() == expected_text.strip()
    print("OK" if exact else "OK (есть расхождения в округлении mean)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
