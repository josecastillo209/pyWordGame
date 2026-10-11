# Word Game – 5×5 Crossword Puzzle

A Python + Tkinter word-guessing game where the player solves a small crossword-style puzzle by discovering three hidden 5-letter words.

## How to Play

1. Launch the game and click **Start Game**.
2. A 5×5 grid appears with certain squares highlighted (these contain the hidden letters).
3. Click a highlighted square and type. Letters flow naturally across or down the current word.
4. Press **Enter** or click **Check Letters**.
5. Feedback is shown immediately:
   - **Green** — correct letter in the correct position (square locks)
   - **Yellow** — letter exists somewhere in the puzzle, but wrong position
   - **Red** — letter is not used in any word in this puzzle
6. The QWERTY keyboard at the bottom updates with the same colors so you can track which letters you’ve tried.
7. Solve all three words to complete the puzzle. A message appears showing how many guesses it took.

## Features Implemented

- Title / start screen
- Randomly generated 5×5 crossword puzzles
- Natural typing flow (auto-advances to the next square in the word)
- Color-coded letter feedback (green / yellow / red)
- Live QWERTY keyboard tracker
- Guess counter
- In-window “Game Complete” message
- Reveal All button (for testing)

## Project Structure

```
pyWordGame/
├── wordgame.py           # Main game (GUI, start screen, gameplay)
├── puzzle_generator.py   # Generates random intersecting puzzles
├── words.txt             # 5-letter word list (Wordle list)
└── .gitignore
```

## Design & Logic

### Puzzle Generation
The generator (`puzzle_generator.py`) builds each puzzle using these rules:

1. Load the word list from `words.txt`.
2. Pick one word at random and place it in the **center** of the grid (middle row or middle column, chosen randomly).
3. Choose a random letter from that word and find a second word that intersects it correctly while staying inside the 5×5 grid.
4. Choose a **different** letter from the first word and place a third intersecting word.
5. If a valid placement can’t be found, the generator retries automatically.

The result is three 5-letter words that cross each other, returned in the format the game expects:

```python
[
    {"word": "APPLE", "positions": [[1,1], [1,2], [1,3], [1,4], [1,5]]},
    {"word": "PLANT", "positions": [[1,3], [2,3], [3,3], [4,3], [5,3]]},
    ...
]
```

### Grid & Input
- The visible grid is built with Tkinter `Entry` widgets for squares that contain letters and `Label` widgets for empty squares.
- A background grid stores the real (hidden) letters.
- Typing advances automatically along the current word. Clicking a square sets the active word (preferring horizontal when a square belongs to both directions).
- Backspace moves backward through the word.

### Letter Feedback
When the player checks their letters:

- Correct position → green + locked
- Letter exists in the puzzle but wrong square → yellow (still editable)
- Letter does not appear in any of the three words → red (still editable)

The same status is reflected on the on-screen QWERTY keyboard.

### Game Flow
- Start screen → Game screen
- Each check increments the guess counter
- When every letter square is correct and locked, an in-window completion message is shown

## Running the Game

```bash
python wordgame.py
```

Requirements:
- Python 3.x
- Tkinter (usually included with Python)

No external packages are required.

## Word List

The word list (`words.txt`) comes from the public [Wordle word list](https://github.com/tabatkins/wordle-list). It contains thousands of valid 5-letter words used by the puzzle generator.

## Future Ideas

- New Puzzle button
- Play Again from the completion screen
- Difficulty settings (more words, larger grid)
- Score / streak tracking
- Sound or simple animations
