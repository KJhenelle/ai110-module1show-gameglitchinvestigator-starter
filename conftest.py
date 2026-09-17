# FIX: Added (empty) root conftest.py using agent mode so pytest adds the
# project root to sys.path, letting tests/test_game_logic.py import
# logic_utils.py without a ModuleNotFoundError.
