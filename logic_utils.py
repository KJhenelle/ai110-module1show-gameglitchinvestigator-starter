# FIX: Refactored logic out of app.py into logic_utils.py using agent mode.
def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    guess_val = int(guess)
    secret_val = int(secret)

    if guess_val == secret_val:
        return "Win", "🎉 Correct!"

    # FIX: high/low hint messages were swapped; agent mode corrected them
    # so "Too High" tells the player to go LOWER and vice versa.
    if guess_val > secret_val:
        return "Too High", "📉 Go LOWER!"

    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


# ---------------------------------------------------------------------------
# Witch JRPG battle rules
# ---------------------------------------------------------------------------

CLOSE_RANGE = 10        # a guess this near the number can land a hit...
LANDING_GUESSES = 2     # ...but only on the first this-many guesses


def attack_power(guess: int, secret: int) -> int:
    """Spell power 0-99: the closer the guess is to the number, the higher."""
    return max(0, 100 - abs(int(guess) - int(secret)))


def spell_lands(guess: int, secret: int, guess_number: int) -> bool:
    """
    A spell lands if the guess is exactly the number, or within CLOSE_RANGE
    on one of the first LANDING_GUESSES guesses at this number.
    """
    distance = abs(int(guess) - int(secret))
    if distance == 0:
        return True
    return distance <= CLOSE_RANGE and guess_number <= LANDING_GUESSES


def spell_damage(guess: int, secret: int) -> int:
    """Damage dealt by a landed spell; an exact hit is a critical strike."""
    power = attack_power(guess, secret)
    return power + 20 if int(guess) == int(secret) else power


def enemy_damage(rng, base: int) -> int:
    """Damage from an enemy counter-attack: base +/- 20%."""
    return max(1, round(base * rng.uniform(0.8, 1.2)))


# ---------------------------------------------------------------------------
# Leveling
# ---------------------------------------------------------------------------

def xp_for_level(level: int) -> int:
    """XP needed to go from `level` to `level + 1`."""
    return 40 * level


def max_hp_for_level(level: int) -> int:
    return 100 + 20 * (level - 1)


def spell_multiplier(level: int) -> float:
    """Landed spells hit 15% harder per level above 1."""
    return 1 + 0.15 * (level - 1)


def add_xp(level: int, xp: int, gained: int):
    """Add XP and return (new_level, new_xp, levels_gained)."""
    xp += gained
    start = level
    while xp >= xp_for_level(level):
        xp -= xp_for_level(level)
        level += 1
    return level, xp, level - start
