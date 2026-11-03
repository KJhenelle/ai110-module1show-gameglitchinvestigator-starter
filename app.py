import random

import streamlit as st
import streamlit.components.v1 as components

import llm
import render
from logic_utils import (
    add_xp,
    attack_power,
    check_guess,
    enemy_damage,
    max_hp_for_level,
    parse_guess,
    spell_damage,
    spell_lands,
    spell_multiplier,
    xp_for_level,
)
from world import MAPS, MONSTERS, try_move

st.set_page_config(page_title="Hexbound: Witch's Gambit", page_icon="🔮")

LOW, HIGH = 1, 100


def show_html(html, height):
    """Embed a self-contained HTML document (st.iframe on new Streamlit)."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height)

st.markdown(
    "<style>.stApp { background: radial-gradient(circle at 50% 0%, #2b1055 0%, "
    "#0f0a1f 70%); } h1, h2, h3, p, label, .stMarkdown, .stCaption "
    "{ color: #f1e7ff !important; }</style>",
    unsafe_allow_html=True,
)


def new_game():
    st.session_state.mode = "explore"
    st.session_state.level = 1
    st.session_state.xp = 0
    st.session_state.player_hp = max_hp_for_level(1)
    st.session_state.area = 0
    st.session_state.pos = MAPS[0]["entry"]
    st.session_state.facing_left = False
    st.session_state.slide = None
    st.session_state.defeated = set()
    st.session_state.msg = "Walk with the arrow keys / WASD or the buttons. Step into a monster to fight it!"
    st.session_state.enemy = None
    st.session_state.enemy_hp = 0
    st.session_state.secret = random.randint(LOW, HIGH)
    st.session_state.attempts = 0       # guesses made at the current number
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.hint = None
    st.session_state.last_event = None  # drives the attack animation
    st.session_state.log = []
    st.session_state.nonce = 0
    st.session_state.number_id = 1
    st.session_state.narration = ""


def enter_area(area, pos):
    st.session_state.area = area
    st.session_state.pos = pos
    # Monsters respawn whenever you re-enter an area, so you can grind XP.
    st.session_state.defeated = {
        d for d in st.session_state.defeated if d[0] != area
    }


def start_battle(code, at):
    mon = MONSTERS[code]
    st.session_state.mode = "battle"
    st.session_state.enemy = dict(mon, at=at, area=st.session_state.area)
    st.session_state.enemy_hp = mon["hp"]
    st.session_state.secret = random.randint(LOW, HIGH)
    st.session_state.attempts = 0
    st.session_state.history = []
    st.session_state.hint = None
    st.session_state.last_event = None
    st.session_state.number_id = 1
    st.session_state.narration = ""
    st.session_state.log = [f"A {mon['name']} blocks your path! Cast your spell!"]


def move(dx, dy):
    ss = st.session_state
    if dx:
        ss.facing_left = dx < 0
    r = try_move(ss.area, ss.pos, dx, dy, ss.level, ss.defeated)
    ss.slide = None
    kind = r["kind"]
    if kind == "move":
        ss.pos = r["pos"]
        ss.slide = (dx, dy)
        ss.msg = ""
        if r["heal"] and ss.player_hp < max_hp_for_level(ss.level):
            ss.player_hp = max_hp_for_level(ss.level)
            ss.msg = "🏠 You rest at the inn and recover all your HP."
    elif kind in ("npc", "locked"):
        ss.msg = r["text"]
    elif kind == "exit":
        enter_area(r["area"], r["pos"])
        ss.slide = None
        ss.msg = f"🗺️ You enter the {MAPS[r['area']]['name']}."
    elif kind == "battle":
        start_battle(r["monster"], r["at"])


if "mode" not in st.session_state:
    new_game()

ss = st.session_state
max_hp = max_hp_for_level(ss.level)

st.title("🔮 Hexbound: Witch's Gambit")

with st.sidebar:
    st.header("🧙‍♀️ Witch")
    st.write(f"Level **{ss.level}**")
    st.caption(f"XP {ss.xp}/{xp_for_level(ss.level)}")
    st.progress(min(1.0, ss.xp / xp_for_level(ss.level)))
    st.caption(f"HP {ss.player_hp}/{max_hp}")
    st.progress(max(0.0, min(1.0, ss.player_hp / max_hp)))
    st.caption(f"Spell damage x{spell_multiplier(ss.level):.2f}")
    if ss.log:
        st.header("📜 Battle Log")
        for line in reversed(ss.log[-10:]):
            st.write(line)
    if st.button("New Game 🔁"):
        new_game()
        st.rerun()

# ===========================================================================
# EXPLORE
# ===========================================================================
if ss.mode == "explore":
    st.subheader(f"📍 {MAPS[ss.area]['name']}")
    show_html(
        render.map_html(ss.area, ss.pos, ss.facing_left, ss.level, ss.defeated, ss.slide),
        height=450,
    )
    if ss.msg:
        st.info(ss.msg)

    _, up, _ = st.columns([3, 1, 3])
    left, down, right = st.columns([1, 1, 1])
    with up:
        st.button("▲", key="up", on_click=move, args=(0, -1), use_container_width=True)
    with left:
        st.button("◀", key="left", on_click=move, args=(-1, 0), use_container_width=True)
    with down:
        st.button("▼", key="down", on_click=move, args=(0, 1), use_container_width=True)
    with right:
        st.button("▶", key="right", on_click=move, args=(1, 0), use_container_width=True)
    st.caption("🔒 Locked gates open as you level up. Beat monsters to earn XP.")
    st.stop()

# ===========================================================================
# BATTLE
# ===========================================================================
enemy = ss.enemy
st.subheader(f"⚔️ {enemy['name']}")
st.caption(
    "Your spell power is how close your guess is to the hidden number (1-100). "
    "Land within 10 on your first 2 guesses, or hit it exactly, and the spell "
    "strikes. Miss and the enemy strikes back!"
)
number_changed = bool(ss.last_event and ss.last_event["kind"] == "player")
show_html(
    render.arena_html(
        enemy["art"], enemy["name"], ss.enemy_hp, enemy["hp"], ss.player_hp,
        max_hp, ss.level, ss.last_event, ss.nonce,
        ss.number_id, number_changed,
    ),
    height=270,
)

if ss.narration:
    st.markdown(f"*{ss.narration}*")
if number_changed:
    st.success(
        f"🔄 The number has changed! It's a brand-new number (#{ss.number_id}). "
        "Your earlier guesses no longer apply."
    )
if ss.history:
    st.caption(f"Guesses at number #{ss.number_id}: {', '.join(map(str, ss.history))}")

guesses_left_to_land = max(0, 2 - ss.attempts)
st.info(
    f"Guess the number between {LOW} and {HIGH}. "
    + (f"Within 10 will land for {guesses_left_to_land} more guess(es)."
       if guesses_left_to_land else "Only an exact guess can land now!")
)

with st.form("cast", clear_on_submit=True):
    raw_guess = st.text_input("Your guess:")
    submit = st.form_submit_button("Cast 🔮")
flee = st.button("Flee 🏃")
show_hint = st.checkbox("Show hint", value=True)

if flee:
    ss.mode = "explore"
    ss.msg = f"You fled from the {enemy['name']}."
    st.rerun()

if submit:
    ok, guess, err = parse_guess(raw_guess)
    if not ok:
        st.error(err)
    else:
        secret = ss.secret
        ss.attempts += 1
        ss.history.append(guess)
        ss.nonce += 1
        power = attack_power(guess, secret)

        if spell_lands(guess, secret, ss.attempts):
            damage = round(spell_damage(guess, secret) * spell_multiplier(ss.level))
            crit = guess == secret
            ss.enemy_hp = max(0, ss.enemy_hp - damage)
            ss.last_event = {"kind": "player", "damage": damage, "crit": crit}
            ss.log.append(
                f"✨ Guess {guess} (power {power}) {'CRIT ' if crit else ''}hits for "
                f"{damage}! The number was {secret}."
            )
            # The number switches once a spell has landed.
            ss.secret = random.randint(LOW, HIGH)
            ss.number_id += 1
            ss.attempts = 0
            ss.history = []
            ss.hint = None

            if ss.enemy_hp <= 0:
                ss.defeated.add((enemy["area"],) + tuple(enemy["at"]))
                ss.level, ss.xp, gained = add_xp(ss.level, ss.xp, enemy["xp"])
                ss.mode = "explore"
                ss.msg = f"🏆 {enemy['name']} defeated! +{enemy['xp']} XP."
                if gained:
                    ss.player_hp = max_hp_for_level(ss.level)
                    ss.msg += f" ⭐ LEVEL UP! You are now level {ss.level} and fully healed."
                    st.toast(f"Level up! Level {ss.level}", icon="⭐")
        else:
            damage = enemy_damage(random, enemy["atk"])
            ss.player_hp = max(0, ss.player_hp - damage)
            ss.last_event = {"kind": "enemy", "damage": damage, "crit": False}
            ss.hint = check_guess(guess, secret)[1]
            ss.log.append(
                f"🩸 Guess {guess} (power {power}) fizzles. "
                f"{enemy['name']} hits you for {damage}."
            )
            if ss.player_hp <= 0:
                # Defeat is not the end: wake up at the area entrance.
                ss.player_hp = max_hp
                ss.pos = MAPS[ss.area]["entry"]
                ss.mode = "explore"
                ss.msg = "💀 You were knocked out... and wake up at the area entrance."
        ev = ss.last_event
        with st.spinner("The narrator inks the scene..."):
            ss.narration, used_llm = llm.narrate({
                "enemy": enemy["name"], "power": power, "damage": ev["damage"],
                "landed": ev["kind"] == "player", "crit": ev["crit"],
                "player_hp": ss.player_hp, "enemy_hp": ss.enemy_hp,
            })
        ss.log.append(f"📖 {ss.narration}")
        st.rerun()

if show_hint and ss.hint and ss.attempts:
    st.warning(ss.hint)

with st.expander("Developer Debug Info"):
    st.write("Secret:", ss.secret)
    st.write("Guesses at this number:", ss.attempts)
    st.write("History:", ss.history)
