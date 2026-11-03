# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🔮 Hexbound: Witch's Gambit (game mode)

Run it with `python -m streamlit run app.py`. The game has two parts.

**Exploring (overworld)**
- Walk a pixel-art witch around a tile map with the arrow keys / WASD (or the on-screen ▲◀▼▶ buttons).
- Trees and water block you, the 🏠 inn heals you, and villagers give hints.
- Step into a monster to start a battle. Winning earns XP; level-ups raise max HP and spell damage.
- Gates are locked until you reach the required level. Level 3 opens the Whispering Woods; a sealed level-6 door is a placeholder for a future area.
- Monsters respawn when you re-enter an area, so you can grind.

**Battling (the number guessing)**
- Guess the hidden number (1-100) to cast a spell. **Spell power = 100 - distance from the number**, so closer guesses hit harder.
- A spell **lands** if the guess is within 10 on your **first 2 guesses** at that number, or is **exact** on any guess (exact = critical hit).
- If the spell doesn't land, the **enemy strikes back** and the number stays the same. When a spell lands, the **number switches**.
- Attacks are animated: a projectile flies across, the target shakes and flashes, and damage floats up.
- Getting knocked out isn't game over: you wake at the area entrance. You can also flee.

**Gemini battle narration (optional)**
- Set `GEMINI_API_KEY` (e.g. `export GEMINI_API_KEY=...` before running, or in `.streamlit/secrets.toml`) to get a one-line narration after every spell. `GEMINI_MODEL` overrides the default `gemini-2.5-flash`.
- The model only sees the outcome (power, damage, HP), never the secret number, and never affects game state. With no key, or if the call fails, canned narration is used.
- When the number switches, the arena badge flashes **NEW NUMBER #n** and a banner appears. Your guesses at the current number are listed so you can see what no longer applies.

Code map: `llm.py` (Gemini narration),  `world.py` (maps, monsters, movement rules), `sprites.py` (pixel art), `render.py` (HTML/SVG builders), `logic_utils.py` (battle and leveling rules), `app.py` (UI and state).

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Game's purpose:** A Streamlit number-guessing game. The player picks a difficulty, gets a secret number in a range, and submits guesses until they either guess correctly ("Win") or run out of attempts, with hints and a running score along the way.
- [x] **Bugs found:**
  - The "Too High"/"Too Low" hint messages were swapped — guessing above the secret told the player to go HIGHER instead of LOWER (and vice versa).
  - `get_range_for_difficulty`, `parse_guess`, and `update_score` were duplicated directly in `app.py` instead of living in `logic_utils.py`, mixing UI and game logic and leaving `logic_utils.py`'s versions as unused `NotImplementedError` stubs.
  - `tests/test_game_logic.py` couldn't import `logic_utils` at all when running `pytest` from the project root, because there was no root `conftest.py`/`pytest.ini` to add the project root to `sys.path`.
  - A few existing tests compared the full `(outcome, message)` tuple returned by `check_guess` to a bare string (e.g. `"Win"`), which never matched.
- [x] **Fixes applied:**
  - Corrected the swapped hint messages in `check_guess` in `logic_utils.py` so "Too High" says "Go LOWER!" and "Too Low" says "Go HIGHER!".
  - Moved `get_range_for_difficulty`, `parse_guess`, and `update_score` fully into `logic_utils.py`, and updated `app.py` to import all four functions from `logic_utils` instead of redefining them.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. User enters a guess of **40** → the app reports **"Too Low"** ("📈 Go HIGHER!"), and the score drops by 5 (score: **-5**).
2. User enters a guess of **70** → the app reports **"Too High"** ("📉 Go LOWER!"), and the score rises by 5 (score: **0**)
3. User enters a guess of **55** → the app reports **"🎉 Correct!"** and declares a win.
4.  The score updates correctly after each guess, using the attempt number to calculate points — in this case, the win on attempt 3 adds 60 points for a **final score of 60**.
5. The game ends: the app shows "You won!" with the secret number and final score, disables further guesses, and only a click on **"New Game"** resets the secret number, attempts, and status so the player can guess again.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
# Paste your pytest output here, e.g.:
# pytest tests/
# ========================= X passed in 0.XXs =========================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
