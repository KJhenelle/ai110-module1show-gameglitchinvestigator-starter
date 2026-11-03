"""Battle narration via the Gemini API, with an offline fallback.

The model only *describes* what already happened. It is never told the secret
number and its output never touches game state.
"""
import json
import os
import urllib.error
import urllib.request

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TIMEOUT = 8  # seconds; the UI blocks while we wait

SYSTEM = (
    "You are the narrator of a witch-themed JRPG. Describe the result of one "
    "spell in ONE vivid sentence (max 25 words). Use only the facts given. "
    "Never reveal or guess any hidden number. No markdown, no quotes."
)


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    try:  # optional: .streamlit/secrets.toml
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def fallback_narration(event):
    """Canned text used when there is no key or the API call fails."""
    enemy = event["enemy"]
    if event["landed"]:
        if event["crit"]:
            return f"A perfect hex! Your spell tears through {enemy} for {event['damage']}!"
        return f"Your spell strikes {enemy} for {event['damage']} damage."
    if event["power"] >= 80:
        return f"So close! The spell fizzles and {enemy} retaliates for {event['damage']}."
    return f"Your spell goes wide. {enemy} strikes back for {event['damage']}!"


def _prompt(event):
    outcome = (
        "a CRITICAL HIT" if event["crit"]
        else "a hit" if event["landed"] else "a miss, so the enemy counter-attacked"
    )
    return (
        f"Enemy: {event['enemy']}. Spell power: {event['power']}/100 "
        f"(higher = closer to the mark). Result: {outcome}. "
        f"Damage dealt to the {'enemy' if event['landed'] else 'witch'}: {event['damage']}. "
        f"Witch HP: {event['player_hp']}. Enemy HP: {event['enemy_hp']}."
    )


def narrate(event, api_key=None, urlopen=urllib.request.urlopen):
    """Return (text, used_llm). Never raises."""
    api_key = api_key or get_api_key()
    if not api_key:
        return fallback_narration(event), False
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"parts": [{"text": _prompt(event)}]}],
        "generationConfig": {
            "maxOutputTokens": 80,
            "temperature": 1.0,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    req = urllib.request.Request(
        URL.format(model=MODEL),
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = json.load(resp)
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if not text:
            raise ValueError("empty")
        return text, True
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError,
            ValueError, OSError):
        return fallback_narration(event), False
