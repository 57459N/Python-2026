"""Генератор входных данных для задачи «Миллиард строк».

Использование:
    python generate_measurements.py N [-o measurements.txt] [--seed 42]

Каждая строка файла имеет вид ``<станция>;<температура>``, где температура —
число от -99.9 до 99.9 ровно с одним знаком после точки. Кодировка UTF-8,
разделитель строк ``\\n``.
"""

import argparse
import random
import sys
import time
from pathlib import Path

STATIONS_FILE = Path(__file__).with_name("weather_stations.csv")
BATCH = 100_000


def load_stations(path: Path) -> list[tuple[str, float]]:
    stations = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            name, mean = line.rstrip("\n").split(";")
            stations.append((name, float(mean)))
    return stations


def generate(n: int, out: Path, seed: int) -> None:
    rng = random.Random(seed)
    stations = load_stations(STATIONS_FILE)
    started = time.perf_counter()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        written = 0
        while written < n:
            size = min(BATCH, n - written)
            lines = []
            for name, mean in rng.choices(stations, k=size):
                tenths = round(rng.gauss(mean, 10.0) * 10)
                tenths = max(-999, min(999, tenths))
                lines.append(f"{name};{tenths / 10:.1f}\n")
            f.write("".join(lines))
            written += size
            if n >= 10 * BATCH and written % (10 * BATCH) == 0:
                print(f"\r{written:,} / {n:,}", end="", file=sys.stderr)
    elapsed = time.perf_counter() - started
    print(f"\rЗаписано {n:,} строк в {out} за {elapsed:.1f} с", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("n", type=lambda s: int(s.replace("_", "")), help="число строк")
    parser.add_argument("-o", "--output", type=Path, default=Path("measurements.txt"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.n, args.output, args.seed)


if __name__ == "__main__":
    main()
