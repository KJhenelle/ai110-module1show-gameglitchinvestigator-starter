"""Pixel art for the overworld and battle arena.

Every sprite is a 12x12 grid of palette letters ('.' is transparent). They
are rendered as crisp SVG so they scale cleanly at any size.
"""

SIZE = 12

PALETTE = {
    "k": "#2b1b3a", "p": "#7b2fbf", "y": "#ffd93d", "s": "#f2c9a0",
    "b": "#15121f", "g": "#5ad65a", "d": "#2e8b3a", "w": "#ffffff",
    "o": "#ff8c1a", "r": "#d62839", "h": "#aab4bf", "a": "#5c6773",
    "t": "#8b5a2b", "l": "#34a853", "m": "#1f7a35", "c": "#ff7ac6",
    "n": "#d9b97a", "e": "#bfdbfe", "i": "#f4a6c0", "v": "#6b7280",
    "z": "#3a3350", "q": "#ffe9a8",
}

TILE_BASE = {
    "grass": "#5fbf5f",
    "path": "#d9b97a",
    "water": "#3b82f6",
}


def _blank(n):
    return ["." * SIZE] * n


WITCH = [
    ".....pp.....",
    "....pppp....",
    "...pppppp...",
    ".yyyyyyyyyy.",
    "...ssssss...",
    "...sbssbs...",
    "...ssssss...",
    "..pppppppp..",
    ".spppyyppps.",
    "..pppppppp..",
    "..pppppppp..",
    "..kk....kk..",
]

SLIME = _blank(2) + [
    "....gggg....",
    "...gggggg...",
    "..gggggggg..",
    ".ggwbggwbgg.",
    ".gggggggggg.",
    ".ggggddgggg.",
    "gggggggggggg",
    "gggggggggggg",
    ".dddddddddd.",
    "............",
]

PUMPKIN = [
    ".....dd.....",
    ".....dd.....",
    "...oooooo...",
    "..oooooooo..",
    ".ooyoooyooo.",
    ".oyyoooyyoo.",
    ".oooooooooo.",
    ".ooykykyoo..",
    ".oooooooooo.",
    "..oooooooo..",
    "...oooooo...",
    "............",
]

KNIGHT = [
    ".....rr.....",
    "....rrr.....",
    "...hhhhhh...",
    "..hhhhhhhh..",
    "..hkkkkkkh..",
    "..hkrkkrkh..",
    "..hhhhhhhh..",
    ".hhaaaaaahh.",
    ".hhaaaaaahh.",
    "..aaaaaaaa..",
    "..aa....aa..",
    "..kk....kk..",
]

VILLAGER = [
    "....tttt....",
    "...tttttt...",
    "...ssssss...",
    "...sbssbs...",
    "...ssssss...",
    "..iiiiiiii..",
    ".siiiiiiiis.",
    "..iiiiiiii..",
    "..iiiiiiii..",
    "..iiiiiiii..",
    "...tt..tt...",
    "............",
]

TREE = [
    "....mmmm....",
    "...mllllm...",
    "..mllllllm..",
    ".mllllllllm.",
    ".mllllllllm.",
    "..mllllllm..",
    "...mmllmm...",
    ".....tt.....",
    ".....tt.....",
    "....tttt....",
    "............",
    "............",
]

FLOWER = _blank(4) + [
    "..c.....c...",
    ".cyc...cyc..",
    "..c.....c...",
    "..d.....d...",
] + _blank(4)

INN = [
    "............",
    "....rrrr....",
    "..rrrrrrrr..",
    ".rrrrrrrrrr.",
    "rrrrrrrrrrrr",
    ".nnnnnnnnnn.",
    ".nwwnnnnwwn.",
    ".nwwnttnwwn.",
    ".nnnnttnnnn.",
    ".nnnnttnnnn.",
    "............",
    "............",
]

GATE_OPEN = [
    "............",
    "..vvvvvvvv..",
    ".vvzzzzzzvv.",
] + [".vzqqqqqqzv."] * 7 + [
    "vvvvvvvvvvvv",
    "............",
]

_LOCK = [
    "............",
    "............",
    "............",
    "............",
    "............",
    "....yyyy....",
    "....y..y....",
    "...yyyyyy...",
    "...yybbyy...",
    "...yyyyyy...",
    "............",
    "............",
]


def _overlay(base, over):
    out = []
    for brow, orow in zip(base, over):
        out.append("".join(o if o != "." else b for b, o in zip(brow, orow)))
    return out


GATE_LOCKED = _overlay([r.replace("q", "z") for r in GATE_OPEN], _LOCK)

WATER_WAVES = _blank(3) + ["...ee....ee."] + _blank(4) + [".ee....ee..."] + _blank(3)

GRASS_SPECKS = [
    _blank(2) + ["..d........."] + _blank(3) + ["........d..."] + _blank(2) + [".d.........."] + _blank(2),
    _blank(1) + ["........d..."] + _blank(4) + ["..d........."] + _blank(2) + ["......d....."] + _blank(2),
    _blank(3) + [".d.........."] + _blank(2) + ["......d....."] + _blank(3) + ["..........d."] + _blank(1),
]

PATH_SPECKS = [
    _blank(3) + ["....t......."] + _blank(4) + [".......t...."] + _blank(3),
    _blank(2) + [".......t...."] + _blank(4) + ["..t........."] + _blank(4),
]

ART = {
    "witch": WITCH, "slime": SLIME, "pumpkin": PUMPKIN, "knight": KNIGHT,
    "villager": VILLAGER, "tree": TREE, "flower": FLOWER, "inn": INN,
    "gate": GATE_OPEN, "gate_locked": GATE_LOCKED, "waves": WATER_WAVES,
}
for _i, _a in enumerate(GRASS_SPECKS):
    ART[f"grass{_i}"] = _a
for _i, _a in enumerate(PATH_SPECKS):
    ART[f"path{_i}"] = _a
ART["witch_l"] = [row[::-1] for row in WITCH]

for _name, _rows in ART.items():
    assert len(_rows) == SIZE, (_name, len(_rows))
    assert all(len(r) == SIZE for r in _rows), _name
    assert all(c == "." or c in PALETTE for r in _rows for c in r), _name


def _rects(rows):
    """Merge horizontal runs of the same colour into single <rect>s."""
    out = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c = row[x]
            if c == ".":
                x += 1
                continue
            start = x
            while x < len(row) and row[x] == c:
                x += 1
            out.append(
                f'<rect x="{start}" y="{y}" width="{x - start}" height="1" '
                f'fill="{PALETTE[c]}"/>'
            )
    return "".join(out)


def symbol(name):
    """An SVG <g id=name> definition for the named art (for use in <defs>)."""
    return f'<g id="{name}">{_rects(ART[name])}</g>'


def sprite_svg(name, px=96):
    """A standalone SVG for one sprite, `px` pixels square."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" '
        f'viewBox="0 0 {SIZE} {SIZE}" shape-rendering="crispEdges">'
        f"{_rects(ART[name])}</svg>"
    )
