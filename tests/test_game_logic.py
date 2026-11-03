from streamlit.testing.v1 import AppTest

from logic_utils import (
    attack_power,
    check_guess,
    enemy_damage,
    spell_damage,
    spell_lands,
    add_xp,
    max_hp_for_level,
    spell_multiplier,
)
from world import MAPS, try_move

# FIX: check_guess returns an (outcome, message) tuple; agent mode updated
# these tests to unpack it instead of comparing the tuple to a bare string.
def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

def test_too_high_message_says_go_lower():
    # Regression test for the glitch: a guess above the secret must be
    # told to go LOWER, not higher.
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message

def test_too_low_message_says_go_higher():
    # Regression test for the glitch: a guess below the secret must be
    # told to go HIGHER, not lower.
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message
    assert "LOWER" not in message

def test_attack_power_rises_as_guess_gets_closer():
    assert attack_power(50, 50) > attack_power(52, 50) > attack_power(80, 50)
    assert attack_power(1, 100) >= 0


def test_spell_lands_within_10_on_first_two_guesses():
    assert spell_lands(58, 50, 1)
    assert spell_lands(40, 50, 2)
    assert not spell_lands(61, 50, 1)


def test_close_guess_misses_after_second_guess_but_exact_still_lands():
    assert not spell_lands(55, 50, 3)
    assert spell_lands(50, 50, 7)


def test_exact_hit_is_a_critical_strike():
    assert spell_damage(50, 50) > spell_damage(51, 50)


def test_enemy_damage_stays_near_base():
    import random
    for _ in range(50):
        assert 9 <= enemy_damage(random, 12) <= 15


def test_add_xp_levels_up_and_carries_over():
    assert add_xp(1, 0, 30) == (1, 30, 0)
    assert add_xp(1, 30, 50) == (2, 40, 1)  # 80 total: 40 to level 2, 40 left
    assert max_hp_for_level(3) > max_hp_for_level(1)
    assert spell_multiplier(3) > spell_multiplier(1)


def test_walls_and_water_block_movement():
    assert try_move(0, (1, 1), 0, -1, 1, set())["kind"] == "blocked"  # tree border
    assert try_move(0, (7, 1), 1, 0, 1, set())["kind"] == "blocked"   # water


def test_walking_onto_open_ground_moves_the_witch():
    r = try_move(0, (1, 1), 1, 0, 1, set())
    assert r == {"kind": "move", "pos": (2, 1), "heal": False}


def test_stepping_into_a_monster_starts_a_battle_unless_defeated():
    assert try_move(0, (6, 2), 0, 1, 1, set())["kind"] == "battle"
    assert try_move(0, (6, 2), 0, 1, 1, {(0, 6, 3)})["kind"] == "move"


def test_gate_is_locked_until_the_required_level():
    assert try_move(0, (6, 7), 0, 1, 2, set())["kind"] == "locked"
    r = try_move(0, (6, 7), 0, 1, 3, set())
    assert r["kind"] == "exit" and r["area"] == 1


def test_sealed_door_is_not_implemented_yet():
    r = try_move(1, (6, 7), 0, 1, 99, set())
    assert r["kind"] == "locked"


def test_inn_heals():
    assert try_move(0, (4, 5), 0, -1, 1, set())["heal"] is True


def test_every_map_row_is_the_same_width_and_exits_are_gates():
    for area, m in enumerate(MAPS):
        assert len({len(r) for r in m["rows"]}) == 1
        for (x, y) in m["exits"]:
            assert m["rows"][y][x] in "GBL"


def _battle(at, **state):
    at.run()
    at.session_state["mode"] = "battle"
    at.session_state["enemy"] = {
        "name": "Bog Slime", "art": "slime", "hp": 150, "atk": 10, "xp": 40,
        "at": (6, 3), "area": 0,
    }
    at.session_state["enemy_hp"] = 150
    at.session_state["secret"] = 50
    for k, v in state.items():
        at.session_state[k] = v
    at.run()


def _cast(at, guess):
    at.text_input[0].set_value(str(guess))
    next(b for b in at.button if "Cast" in b.label).click().run()


def test_landed_spell_damages_enemy_and_switches_number():
    at = AppTest.from_file("../app.py", default_timeout=120)
    _battle(at)
    _cast(at, 55)
    assert at.session_state["enemy_hp"] < 150
    assert at.session_state["last_event"]["kind"] == "player"
    assert at.session_state["attempts"] == 0  # number switched


def test_missed_spell_hurts_the_witch():
    at = AppTest.from_file("../app.py", default_timeout=120)
    _battle(at)
    _cast(at, 99)
    assert at.session_state["player_hp"] < 100
    assert at.session_state["last_event"]["kind"] == "enemy"
    assert at.session_state["secret"] == 50  # number stays until guessed


def test_defeating_a_monster_gives_xp_and_returns_to_the_map():
    at = AppTest.from_file("../app.py", default_timeout=120)
    _battle(at, enemy_hp=1)
    _cast(at, 50)
    assert at.session_state["mode"] == "explore"
    assert at.session_state["level"] == 2  # 40 XP is exactly level 2
    assert at.session_state["player_hp"] == 120  # level up heals fully
    assert (0, 6, 3) in at.session_state["defeated"]


def test_knocked_out_witch_wakes_at_entrance_with_full_hp():
    at = AppTest.from_file("../app.py", default_timeout=120)
    _battle(at, player_hp=1)
    _cast(at, 99)
    assert at.session_state["mode"] == "explore"
    assert at.session_state["player_hp"] == 100
    assert at.session_state["pos"] == MAPS[0]["entry"]


def test_stepping_into_a_monster_in_the_app_starts_a_battle():
    at = AppTest.from_file("../app.py", default_timeout=120)
    at.run()
    at.session_state["pos"] = (6, 2)
    next(b for b in at.button if b.label == "\u25bc").click().run()
    assert at.session_state["mode"] == "battle"
    assert at.session_state["enemy"]["name"] == "Bog Slime"


def test_flee_returns_to_the_map():
    at = AppTest.from_file("../app.py", default_timeout=120)
    _battle(at)
    next(b for b in at.button if "Flee" in b.label).click().run()
    assert at.session_state["mode"] == "explore"
