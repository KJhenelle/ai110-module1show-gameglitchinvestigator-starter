"""HTML builders for the overworld map and the battle arena.

These return self-contained documents meant for an iframe, so styles and
animations are not touched by Streamlit's markdown sanitising.
"""
import sprites
from world import MAPS, MONSTERS, map_size

T = sprites.SIZE  # one tile in SVG units

_BASE_CSS = """
html, body { margin: 0; background: transparent; font-family: system-ui, sans-serif; }
svg { display: block; }
"""

_KEY_JS = """
<script>
(function () {
  var doc;
  try { doc = window.parent.document; } catch (e) { return; }
  var win = window.parent;
  if (win.__hexKeys) doc.removeEventListener('keydown', win.__hexKeys);
  var map = {ArrowUp: '▲', w: '▲', ArrowDown: '▼', s: '▼',
             ArrowLeft: '◀', a: '◀', ArrowRight: '▶', d: '▶'};
  win.__hexKeys = function (ev) {
    var tag = (ev.target && ev.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;
    var label = map[ev.key] || map[(ev.key || '').toLowerCase()];
    if (!label) return;
    var btns = doc.querySelectorAll('button');
    for (var i = 0; i < btns.length; i++) {
      if (btns[i].textContent.trim() === label) {
        ev.preventDefault();
        btns[i].click();
        return;
      }
    }
  };
  doc.addEventListener('keydown', win.__hexKeys);
})();
</script>
"""


def _defs(names):
    return "<defs>" + "".join(sprites.symbol(n) for n in names) + "</defs>"


def _cell(x, y, ch, area, level, defeated):
    """SVG for one map tile (terrain + any static object)."""
    px, py = x * T, y * T
    base = "path" if ch in (",", "G", "B", "L") else "grass"
    if ch == "~":
        base = "water"
    out = [f'<rect x="{px}" y="{py}" width="{T}" height="{T}" fill="{sprites.TILE_BASE[base]}"/>']

    def use(name):
        out.append(f'<use href="#{name}" x="{px}" y="{py}"/>')

    if base == "grass":
        use(f"grass{(x * 7 + y * 13) % 3}")
    elif base == "path":
        use(f"path{(x * 5 + y * 3) % 2}")
    elif base == "water":
        use("waves")

    if ch == "#":
        use("tree")
    elif ch == "f":
        use("flower")
    elif ch == "H":
        use("inn")
    elif ch == "N":
        use("villager")
    elif ch in ("G", "B", "L"):
        _, req, _ = MAPS[area]["exits"][(x, y)]
        sealed = MAPS[area]["exits"][(x, y)][0] is None
        use("gate_locked" if sealed or level < req else "gate")
    return "".join(out)


def map_html(area, pos, facing_left, level, defeated, slide=None):
    """The overworld: tiles, monsters and the witch, with key controls."""
    m = MAPS[area]
    w, h = map_size(area)
    cells, monsters = [], []
    for y, row in enumerate(m["rows"]):
        for x, ch in enumerate(row):
            cells.append(_cell(x, y, ch, area, level, defeated))
            if ch in MONSTERS and (area, x, y) not in defeated:
                delay = ((x * 3 + y) % 5) * 0.2
                monsters.append(
                    f'<g transform="translate({x * T},{y * T})">'
                    f'<g class="bob" style="animation-delay:{delay}s">'
                    f'<use href="#{MONSTERS[ch]["art"]}"/></g></g>'
                )

    dx, dy = slide or (0, 0)
    witch = "witch_l" if facing_left else "witch"
    player = (
        f'<g transform="translate({pos[0] * T},{pos[1] * T})">'
        f'<g class="step" style="--dx:{-dx * T}px;--dy:{-dy * T}px">'
        f'<g class="bob"><use href="#{witch}"/></g></g></g>'
    )

    arts = ["grass0", "grass1", "grass2", "path0", "path1", "waves", "tree",
            "flower", "inn", "villager", "gate", "gate_locked", "witch",
            "witch_l", "slime", "pumpkin", "knight"]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{_BASE_CSS}
svg {{ width: 100%; max-width: {w * 48}px; margin: 0 auto; border: 3px solid #8b5cf6;
  border-radius: 10px; box-sizing: border-box; background: #140c2b; }}
.bob {{ animation: bob 0.9s ease-in-out infinite; }}
.step {{ animation: step 0.16s linear; }}
@keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-0.7px); }} }}
@keyframes step {{ from {{ transform: translate(var(--dx), var(--dy)); }} to {{ transform: translate(0,0); }} }}
</style></head><body>
<svg viewBox="0 0 {w * T} {h * T}" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
{_defs(arts)}{''.join(cells)}{''.join(monsters)}{player}</svg>
{_KEY_JS}</body></html>"""


def arena_html(sprite, enemy_name, enemy_hp, enemy_max, player_hp, player_max,
               level, event, nonce, number_id=1, number_changed=False):
    """The battle scene with projectile / hit / damage-number animations."""
    bolt = dmg = ""
    hit_player = hit_enemy = ""
    if event:
        if event["kind"] == "player":
            bolt = '<div class="bolt right">🔮</div>'
            hit_enemy = " hit"
            crit = " CRIT!" if event["crit"] else ""
            dmg = f'<div class="dmg onenemy">-{event["damage"]}{crit}</div>'
        else:
            bolt = '<div class="bolt left">💥</div>'
            hit_player = " hit"
            dmg = f'<div class="dmg onplayer">-{event["damage"]}</div>'

    def bar(cur, mx, cls):
        pct = max(0, min(100, cur / mx * 100))
        return f'<div class="bar {cls}"><div style="width:{pct}%"></div></div>'

    badge = (
        f'<div class="badge new">🔄 NEW NUMBER #{number_id}</div>' if number_changed
        else f'<div class="badge">🔮 Number #{number_id}</div>'
    )

    return f"""<!doctype html><html><head><meta charset="utf-8"><!-- {nonce} --><style>
{_BASE_CSS}
body {{ color: #f1e7ff; background: #0f0a1f; border-radius: 12px; }}
.arena {{ position: relative; display: flex; justify-content: space-between;
  align-items: flex-end; height: 170px; padding: 0 36px; border: 3px solid #8b5cf6;
  background: linear-gradient(#1b1138, #2a1a55); border-radius: 12px; overflow: hidden; }}
.arena::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 26px; background: #140c2b; }}
.fighter {{ z-index: 2; margin-bottom: 14px; }}
.fighter.hit {{ animation: shake .5s .55s, flash .5s .55s; }}
.bolt {{ position: absolute; bottom: 70px; font-size: 44px; z-index: 3; opacity: 0;
  animation-duration: .6s; animation-fill-mode: forwards; animation-timing-function: ease-in; }}
.bolt.right {{ left: 120px; animation-name: flyRight; }}
.bolt.left {{ right: 120px; animation-name: flyLeft; }}
.dmg {{ position: absolute; top: 12px; font-size: 34px; font-weight: 800; z-index: 4; opacity: 0;
  animation: floatUp 1.1s .55s forwards; }}
.dmg.onenemy {{ right: 50px; color: #ffd166; text-shadow: 0 0 10px #ff9f1c; }}
.dmg.onplayer {{ left: 50px; color: #ff5d73; text-shadow: 0 0 10px #c1121f; }}
.badge {{ position: absolute; top: 8px; left: 50%; transform: translateX(-50%); z-index: 5;
  padding: 4px 12px; border-radius: 999px; font-size: 13px; font-weight: 700;
  background: #2d2250; border: 1px solid #6d4aff; color: #cdbdff; }}
.badge.new {{ background: #ffd166; color: #3a2400; border-color: #ff9f1c;
  animation: pulse .6s 1.1s 4; }}
@keyframes pulse {{ 50% {{ transform: translateX(-50%) scale(1.25); box-shadow: 0 0 16px #ffd166; }} }}
.row {{ display: flex; gap: 16px; margin-top: 10px; }}
.row > div {{ flex: 1; font-size: 14px; }}
.bar {{ background: #2d2250; border-radius: 8px; height: 14px; overflow: hidden; border: 1px solid #6d4aff; margin-top: 4px; }}
.bar > div {{ height: 100%; }}
.hpp > div {{ background: linear-gradient(90deg, #7bd88f, #38b000); }}
.hpe > div {{ background: linear-gradient(90deg, #ff6b6b, #c1121f); }}
@keyframes flyRight {{ 0% {{ left: 120px; opacity: 1; transform: scale(.6) rotate(0); }}
  100% {{ left: calc(100% - 190px); opacity: 1; transform: scale(1.3) rotate(360deg); }} }}
@keyframes flyLeft {{ 0% {{ right: 120px; opacity: 1; transform: scale(.6); }}
  100% {{ right: calc(100% - 190px); opacity: 1; transform: scale(1.3); }} }}
@keyframes shake {{ 0%,100% {{ transform: translateX(0); }} 20% {{ transform: translateX(-12px); }}
  40% {{ transform: translateX(12px); }} 60% {{ transform: translateX(-8px); }} 80% {{ transform: translateX(8px); }} }}
@keyframes flash {{ 50% {{ filter: brightness(3) saturate(0); }} }}
@keyframes floatUp {{ 0% {{ opacity: 1; transform: translateY(30px); }} 100% {{ opacity: 0; transform: translateY(-20px); }} }}
</style></head><body>
<div class="arena">{badge}{bolt}{dmg}
  <div class="fighter{hit_player}">{sprites.sprite_svg("witch", 96)}</div>
  <div class="fighter{hit_enemy}">{sprites.sprite_svg(sprite, 96)}</div>
</div>
<div class="row">
  <div><b>🧙‍♀️ Witch Lv {level}</b> — {player_hp}/{player_max} HP{bar(player_hp, player_max, "hpp")}</div>
  <div><b>{enemy_name}</b> — {enemy_hp}/{enemy_max} HP{bar(enemy_hp, enemy_max, "hpe")}</div>
</div>
</body></html>"""
