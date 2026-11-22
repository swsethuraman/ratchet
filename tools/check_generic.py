"""Fail if game-specific identifiers leak into the agent.

The hidden 55 games are novel; anything tuned to a public game's identity is
overfitting. Populate config/game_ids.txt from `make list-games` (one 4-char
game id per line). CI runs this on every PR.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    ids_file = ROOT / "config" / "game_ids.txt"
    ids = [l.strip() for l in ids_file.read_text().splitlines() if l.strip() and not l.startswith("#")] if ids_file.exists() else []
    if not ids:
        print("check_generic: config/game_ids.txt empty -- populate it from `make list-games`")
        return 0
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, ids)) + r")\b")
    bad = []
    for path in (ROOT / "agent").rglob("*.py"):
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if pattern.search(line):
                bad.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()}")
    if bad:
        print("Game-specific identifiers found in agent/:\n" + "\n".join(bad))
        return 1
    print(f"check_generic: clean ({len(ids)} game ids checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
