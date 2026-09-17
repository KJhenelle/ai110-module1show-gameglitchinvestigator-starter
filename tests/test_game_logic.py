from streamlit.testing.v1 import AppTest

from logic_utils import check_guess

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

# FIX: written in agent mode alongside the app.py fix where "New Game"
# wasn't resetting status back to "playing", which left the app stuck
# on the game-over screen and unable to accept new guesses.
def test_new_game_allows_guessing_after_a_win():
    # Regression test for the glitch: after winning, clicking "New Game"
    # must let the player submit guesses again instead of leaving the
    # app stuck on "Game over" / "You already won".
    at = AppTest.from_file("../app.py")
    at.run()

    # Force the current round into a "won" state without playing it out.
    at.session_state["status"] = "won"

    # Click "New Game".
    new_game_button = next(
        b for b in at.button if "New Game" in b.label
    )
    new_game_button.click().run()

    assert at.session_state["status"] == "playing"

    # Submitting a guess should now be processed instead of the app
    # stopping early on the stale "won"/"lost" status.
    guess_inputs = [w for w in at.text_input]
    assert guess_inputs, "Expected a guess text input to be rendered"
    guess_inputs[0].set_value("1").run()

    submit_button = next(
        b for b in at.button if "Submit Guess" in b.label
    )
    submit_button.click().run()

    assert at.session_state["attempts"] == 1

# FIX: written in agent mode alongside the app.py fix that moved the
# "Developer Debug Info" expander below the submit-processing block.
def test_debug_info_reflects_guess_in_the_same_run():
    # Regression test for the glitch: the "Developer Debug Info" expander
    # used to be rendered ABOVE the guess-processing code, so a submitted
    # guess wasn't reflected in the debug attempts/history until the next
    # rerun. It must now show the up-to-date state on the very same run
    # the guess was submitted in.
    at = AppTest.from_file("../app.py")
    at.run()

    guess_inputs = [w for w in at.text_input]
    assert guess_inputs, "Expected a guess text input to be rendered"
    guess_inputs[0].set_value("1").run()

    submit_button = next(
        b for b in at.button if "Submit Guess" in b.label
    )
    submit_button.click().run()

    # The underlying state updated as expected.
    assert at.session_state["attempts"] == 1
    assert at.session_state["history"] == [1]

    # And the debug expander, rendered in this same run, already reflects it.
    debug_expander = next(e for e in at.expander if "Debug" in e.label)
    debug_text = " ".join(m.value for m in debug_expander.markdown)

    assert "Attempts: `1`" in debug_text
    assert debug_expander.json[0].value == "[1]"
