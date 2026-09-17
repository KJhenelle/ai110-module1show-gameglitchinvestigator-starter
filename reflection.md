# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  
  - the hints were backward
  - High difficulty easier than normal difficulty
  - New game button does not start new game
  - you get 1 less guess than you're meant to 

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| number higher than target| hint says go lower| hint says go higher|None|
| Harder difficulty| Expanded range of numbers| reduced range of numbers| None|
| New game | start new game and allow more inputs| remains in game over mode | None |
|input guess|add to history|adds to history after next guess|None|
---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  - Claude code
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  - AI suggested to move the developer debug info underneath the rest of the code so that it gets updated with each input and keeps an exact history.
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
  - the AI attempted to add the tests directly to the app.py instead of test_game_logic.py

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  I decided a bug was fixed when it would not appear any more in the app and it also passed the pytest
  and what it showed you about your code.
It showed that my code was testable and performing as expected
- Did AI help you design or understand any tests? How?
AI help me design the test for the UI tests of the debugger It used to do it, which is an API wasn't aware of.
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
Rerun runs the entire code from top to bottom every time you click a button or enter information into a field
Session serves to keep the information from getting deleted each rerun
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  Separating game logic from UI component in separate files to increase readability and cleanliness of code
- What is one thing you would do differently next time you work with AI on a coding task?
I would provide the AI with specific functions to work on and specific instructions so that it does not edit anything but what I want it to.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
  It made me aware of the importance of checking everything AI produces to ensure that it's doing what you expected it to do. the AI is able to do a lot of work, however it will assume different parts of your project are more similar to what it's trained on if you don't correct and specifically tailor your prompt to what you're working on.
