"""Overworld maps, monsters and (pure) movement rules."""

# Tile legend
#   #  tree (blocked)        ~  water (blocked)
#   .  grass                 ,  path          f  flowers
#   H  inn (walk in to heal) N  villager (talk)
#   S C K  monster spawns    G B L  gates / sealed door
BLOCKING = {"#", "~"}

MONSTERS = {
    "S": {"name": "Bog Slime", "art": "slime", "hp": 150, "atk": 10, "xp": 40},
    "C": {"name": "Haunted Pumpkin", "art": "pumpkin", "hp": 220, "atk": 14, "xp": 70},
    "K": {"name": "Cursed Knight", "art": "knight", "hp": 300, "atk": 18, "xp": 110},
}

MAPS = [
    {
        "name": "Hollow Meadow",
        "entry": (1, 1),
        "rows": [
            "############",
            "#P..f...~~~#",
            "#.,,,,,.~~.#",
            "#.,##.S..f.#",
            "#.,.H..,,,.#",
            "#S,..f.,.S.#",
            "#.,,,,,,.N.#",
            "#f..S..f...#",
            "######G#####",
        ],
        "npc": {
            (9, 6): "Villager: Slimes in the meadow are easy pickings. Reach "
                    "level 3 and the gate south will open into the woods!",
        },
        # gate tile -> (destination area, required level, arrival tile)
        "exits": {(6, 8): (1, 3, (6, 1))},
    },
    {
        "name": "Whispering Woods",
        "entry": (6, 1),
        "rows": [
            "######B#####",
            "#...,,,,..f#",
            "#.#.,##,.#.#",
            "#.C.,..,.C.#",
            "#f..,,,,..f#",
            "#.##.....#.#",
            "#.C.N.K.~~.#",
            "#f.......~~#",
            "######L#####",
        ],
        "npc": {
            (4, 6): "Wanderer: A sealed door lies south. They say you need "
                    "level 6 to break the hex. The knight guards the way.",
        },
        "exits": {
            (6, 0): (0, 1, (6, 7)),
            (6, 8): (None, 6, None),  # sealed: not implemented yet
        },
    },
]

for _m in MAPS:
    assert len({len(r) for r in _m["rows"]}) == 1, _m["name"]


def map_size(area):
    rows = MAPS[area]["rows"]
    return len(rows[0]), len(rows)


def try_move(area, pos, dx, dy, level, defeated):
    """
    Work out what happens when the player tries to step (dx, dy).

    Returns a dict with a "kind": blocked | move | npc | battle | locked | exit.
    """
    m = MAPS[area]
    w, h = map_size(area)
    nx, ny = pos[0] + dx, pos[1] + dy
    if not (0 <= nx < w and 0 <= ny < h):
        return {"kind": "blocked"}

    ch = m["rows"][ny][nx]
    if ch in BLOCKING:
        return {"kind": "blocked"}

    if ch == "N":
        return {"kind": "npc", "text": m["npc"].get((nx, ny), "...")}

    if ch in MONSTERS and (area, nx, ny) not in defeated:
        return {"kind": "battle", "monster": ch, "at": (nx, ny)}

    if ch in ("G", "B", "L"):
        dest, req, arrive = m["exits"][(nx, ny)]
        if dest is None:
            return {
                "kind": "locked",
                "text": f"🔒 A sealed door hums with dark magic (level {req}). "
                        "This area is coming soon!",
            }
        if level < req:
            return {
                "kind": "locked",
                "text": f"🔒 The gate is sealed. Reach level {req} to pass "
                        f"(you are level {level}).",
            }
        return {"kind": "exit", "area": dest, "pos": arrive}

    return {"kind": "move", "pos": (nx, ny), "heal": ch == "H"}
