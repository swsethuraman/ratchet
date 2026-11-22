"""Perception front-end: turn raw 64x64 frames into objects and events.

Pixels are the wrong unit; objects and events are the right ones. This module is
deliberately generic -- core-knowledge primitives only (objectness, motion,
appearance/disappearance). It must never contain game-specific logic.

Known limitation (by design, see docs/PROGRAMME.md "Caveat 1"): same-colour
4-connected components mis-segment multi-coloured sprites and dotted counters.
The agent must always be able to request a raw crop when hypotheses stop fitting.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field

Grid = list[list[int]]


@dataclass(frozen=True)
class Obj:
    color: int
    cells: frozenset[tuple[int, int]]  # (x, y)

    @property
    def size(self) -> int:
        return len(self.cells)

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        xs = [c[0] for c in self.cells]
        ys = [c[1] for c in self.cells]
        return min(xs), min(ys), max(xs), max(ys)

    @property
    def origin(self) -> tuple[int, int]:
        x0, y0, _, _ = self.bbox
        return x0, y0

    @property
    def centroid(self) -> tuple[float, float]:
        n = len(self.cells)
        return (sum(c[0] for c in self.cells) / n, sum(c[1] for c in self.cells) / n)

    @property
    def shape(self) -> frozenset[tuple[int, int]]:
        """Cells relative to the bbox origin: identical for translated copies."""
        x0, y0 = self.origin
        return frozenset((x - x0, y - y0) for x, y in self.cells)


def latest_grid(frame) -> Grid:
    """Frames arrive as a list of 2D grids (animation); the last is the settled state."""
    if frame and isinstance(frame[0], list) and frame[0] and isinstance(frame[0][0], list):
        return frame[-1]
    return frame


def background_color(grid: Grid) -> int:
    return Counter(v for row in grid for v in row).most_common(1)[0][0]


def segment(grid: Grid, background: int | None = None) -> list[Obj]:
    """Same-colour 4-connected components, excluding the background colour."""
    bg = background_color(grid) if background is None else background
    h, w = len(grid), len(grid[0])
    seen = [[False] * w for _ in range(h)]
    objs: list[Obj] = []
    for y in range(h):
        for x in range(w):
            if seen[y][x] or grid[y][x] == bg:
                continue
            color = grid[y][x]
            cells = []
            q = deque([(x, y)])
            seen[y][x] = True
            while q:
                cx, cy = q.popleft()
                cells.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and grid[ny][nx] == color:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            objs.append(Obj(color, frozenset(cells)))
    objs.sort(key=lambda o: (o.origin[1], o.origin[0], o.color))
    return objs


@dataclass
class StepEvents:
    moved: dict[int, tuple[int, int]] = field(default_factory=dict)  # id -> (dx, dy)
    appeared: list[int] = field(default_factory=list)
    vanished: list[int] = field(default_factory=list)
    changed_cells: int = 0

    @property
    def nothing_happened(self) -> bool:
        return self.changed_cells == 0


class Tracker:
    """Assigns stable IDs to objects across frames and reports per-step events.

    Matching: same colour and same shape -> nearest by origin (a translation).
    Unmatched objects are reported as appeared / vanished. Greedy, deliberately simple.
    """

    def __init__(self) -> None:
        self.objects: dict[int, Obj] = {}
        self._next_id = 1
        self._prev_grid: Grid | None = None

    def update(self, grid: Grid) -> StepEvents:
        current = segment(grid)
        ev = StepEvents()
        if self._prev_grid is not None:
            ev.changed_cells = sum(
                1
                for row_a, row_b in zip(self._prev_grid, grid)
                for a, b in zip(row_a, row_b)
                if a != b
            )
        unmatched_prev = dict(self.objects)
        new_objects: dict[int, Obj] = {}
        for obj in current:
            candidates = [
                (oid, p)
                for oid, p in unmatched_prev.items()
                if p.color == obj.color and p.shape == obj.shape
            ]
            if candidates:
                oid, p = min(
                    candidates,
                    key=lambda c: abs(c[1].origin[0] - obj.origin[0]) + abs(c[1].origin[1] - obj.origin[1]),
                )
                del unmatched_prev[oid]
                dx, dy = obj.origin[0] - p.origin[0], obj.origin[1] - p.origin[1]
                if (dx, dy) != (0, 0):
                    ev.moved[oid] = (dx, dy)
                new_objects[oid] = obj
            else:
                oid = self._next_id
                self._next_id += 1
                new_objects[oid] = obj
                if self._prev_grid is not None:
                    ev.appeared.append(oid)
        ev.vanished = sorted(unmatched_prev)
        self.objects = new_objects
        self._prev_grid = [row[:] for row in grid]
        return ev


def describe(tracker: Tracker, ev: StepEvents, max_objects: int = 40) -> str:
    """Compact text for an LLM: objects plus what changed this step."""
    lines = ["Objects:"]
    for oid, o in list(sorted(tracker.objects.items()))[:max_objects]:
        x0, y0, x1, y1 = o.bbox
        tag = f" moved {ev.moved[oid]}" if oid in ev.moved else ""
        lines.append(f"  #{oid} colour {o.color} {x1 - x0 + 1}x{y1 - y0 + 1} at ({x0},{y0}){tag}")
    if ev.appeared:
        lines.append(f"Appeared: {ev.appeared}")
    if ev.vanished:
        lines.append(f"Vanished: {ev.vanished}")
    if ev.nothing_happened:
        lines.append("Nothing changed.")
    return "\n".join(lines)
