"""Perception validated on synthetic frames with known answers."""

from agent.perception import Tracker, background_color, describe, latest_grid, segment


def blank(n=16, bg=0):
    return [[bg] * n for _ in range(n)]


def paint(grid, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            grid[yy][xx] = color
    return grid


def test_background_is_most_common_colour():
    g = paint(blank(bg=5), 1, 1, 2, 2, 9)
    assert background_color(g) == 5


def test_segments_separate_objects_and_ignores_background():
    g = blank()
    paint(g, 1, 1, 3, 3, 9)
    paint(g, 10, 10, 1, 4, 2)
    objs = segment(g)
    assert len(objs) == 2
    assert {o.color for o in objs} == {9, 2}
    assert {o.size for o in objs} == {9, 4}


def test_same_colour_touching_is_one_object_diagonal_is_two():
    g = blank()
    paint(g, 2, 2, 2, 1, 7)
    paint(g, 4, 2, 2, 1, 7)  # touching horizontally -> one object
    g[8][8] = 7
    g[9][9] = 7  # diagonal only -> two objects
    assert len(segment(g)) == 3


def test_tracker_reports_translation_with_stable_id():
    t = Tracker()
    g0 = paint(blank(), 5, 5, 2, 2, 9)
    t.update(g0)
    (oid,) = t.objects.keys()
    g1 = paint(blank(), 5, 4, 2, 2, 9)  # moved up by one
    ev = t.update(g1)
    assert ev.moved == {oid: (0, -1)}
    assert list(t.objects.keys()) == [oid]


def test_tracker_reports_appear_and_vanish():
    t = Tracker()
    g0 = paint(blank(), 1, 1, 1, 1, 3)
    t.update(g0)
    (old,) = t.objects.keys()
    g1 = paint(blank(), 8, 8, 2, 2, 4)
    ev = t.update(g1)
    assert ev.vanished == [old]
    assert len(ev.appeared) == 1


def test_no_change_is_detected():
    t = Tracker()
    g = paint(blank(), 2, 2, 2, 2, 9)
    t.update(g)
    ev = t.update([row[:] for row in g])
    assert ev.nothing_happened
    assert "Nothing changed." in describe(t, ev)


def test_latest_grid_takes_last_animation_frame():
    a, b = blank(4), paint(blank(4), 0, 0, 1, 1, 9)
    assert latest_grid([a, b]) is b
    assert latest_grid(a) is a
