import tkinter as tk
from puzzle_generator import load_words, generate_puzzle

# ===== Load words and generate a puzzle =====
ALL_WORDS = load_words("words.txt")
WORDS_DATA = generate_puzzle(ALL_WORDS)

# Fallback if generation fails
if WORDS_DATA is None:
    WORDS_DATA = [
        {"word": "APPLE", "positions": [[1,1],[1,2],[1,3],[1,4],[1,5]]},
        {"word": "PLANT", "positions": [[1,3],[2,3],[3,3],[4,3],[5,3]]},
        {"word": "GRAPE", "positions": [[3,1],[3,2],[3,3],[3,4],[3,5]]},
    ]


def create_game(root):
    """Builds the actual game screen inside the given parent."""
    game_frame = tk.Frame(root)

    title = tk.Label(game_frame, text="5×5 Crossword Grid", font=("Arial", 16, "bold"))
    title.pack(pady=10)

    # Guesses tracker
    guesses = [0]
    guesses_label = tk.Label(game_frame, text="Guesses: 0", font=("Arial", 12))
    guesses_label.pack(pady=(0, 5))

    # Status / completion message
    status_label = tk.Label(game_frame, text="", font=("Arial", 14, "bold"), fg="#2e7d32")
    status_label.pack(pady=(0, 10))

    grid_frame = tk.Frame(game_frame, padx=10, pady=10)
    grid_frame.pack()

    # Background grid
    background_grid = [[None for _ in range(5)] for _ in range(5)]
    for word_info in WORDS_DATA:
        word = word_info["word"]
        for i, (r, c) in enumerate(word_info["positions"]):
            background_grid[r-1][c-1] = word[i]

    # Map each cell to the word(s) it belongs to
    cell_to_words = {}
    for word_idx, word_info in enumerate(WORDS_DATA):
        for pos_idx, (r, c) in enumerate(word_info["positions"]):
            key = (r-1, c-1)
            if key not in cell_to_words:
                cell_to_words[key] = []
            cell_to_words[key].append((word_idx, pos_idx))

    cells = []
    for row in range(5):
        row_cells = []
        for col in range(5):
            has_letter = background_grid[row][col] is not None

            if has_letter:
                cell = tk.Entry(
                    grid_frame,
                    width=3,
                    font=("Arial", 18, "bold"),
                    justify="center",
                    relief="ridge",
                    borderwidth=2,
                    bg="#fff9c4"
                )
                vcmd = (root.register(lambda s: len(s) <= 1), "%P")
                cell.config(validate="key", validatecommand=vcmd)
            else:
                cell = tk.Label(
                    grid_frame,
                    text="",
                    width=4,
                    height=2,
                    font=("Arial", 18, "bold"),
                    relief="flat",
                    bg="#e0e0e0"
                )

            cell.grid(row=row, column=col, padx=2, pady=2)
            row_cells.append(cell)
        cells.append(row_cells)

    # Track current word being typed
    current_word_idx = [None]
    current_pos = [0]

    def get_next_entry(word_idx, pos_idx):
        positions = WORDS_DATA[word_idx]["positions"]
        if pos_idx + 1 < len(positions):
            nr, nc = positions[pos_idx + 1]
            return cells[nr-1][nc-1]
        return None

    def get_prev_entry(word_idx, pos_idx):
        positions = WORDS_DATA[word_idx]["positions"]
        if pos_idx - 1 >= 0:
            pr, pc = positions[pos_idx - 1]
            return cells[pr-1][pc-1]
        return None

    def on_key(event, row, col):
        entry = cells[row][col]
        if not isinstance(entry, tk.Entry) or str(entry.cget("state")) == "disabled":
            return "break"

        key = (row, col)
        word_options = cell_to_words.get(key, [])
        if not word_options:
            return "break"

        chosen = None
        if current_word_idx[0] is not None:
            for w_idx, p_idx in word_options:
                if w_idx == current_word_idx[0]:
                    chosen = (w_idx, p_idx)
                    break
        if chosen is None:
            chosen = word_options[0]

        w_idx, p_idx = chosen
        current_word_idx[0] = w_idx
        current_pos[0] = p_idx

        if event.keysym == "BackSpace":
            entry.delete(0, tk.END)
            prev_entry = get_prev_entry(w_idx, p_idx)
            if prev_entry and isinstance(prev_entry, tk.Entry):
                current_word_idx[0] = w_idx
                current_pos[0] = p_idx - 1
                prev_entry.focus_set()
                prev_entry.select_range(0, tk.END)
            return "break"

        if event.char.isalpha():
            entry.delete(0, tk.END)
            entry.insert(0, event.char.upper())
            next_entry = get_next_entry(w_idx, p_idx)
            if next_entry and isinstance(next_entry, tk.Entry) and str(next_entry.cget("state")) != "disabled":
                current_word_idx[0] = w_idx
                current_pos[0] = p_idx + 1
                next_entry.focus_set()
                next_entry.select_range(0, tk.END)
            return "break"

        return "break"

    for r in range(5):
        for c in range(5):
            if isinstance(cells[r][c], tk.Entry):
                cells[r][c].bind("<Key>", lambda e, row=r, col=c: on_key(e, row, col))

    def on_click(event, row, col):
        key = (row, col)
        options = cell_to_words.get(key, [])
        if options:
            preferred = options[0]
            for opt in options:
                w_idx = opt[0]
                positions = WORDS_DATA[w_idx]["positions"]
                if positions[0][0] == positions[-1][0]:  # horizontal
                    preferred = opt
                    break
            current_word_idx[0] = preferred[0]
            current_pos[0] = preferred[1]

    for r in range(5):
        for c in range(5):
            if isinstance(cells[r][c], tk.Entry):
                cells[r][c].bind("<Button-1>", lambda e, row=r, col=c: on_click(e, row, col))

    def is_puzzle_complete():
        for r in range(5):
            for c in range(5):
                if background_grid[r][c] is None:
                    continue
                entry = cells[r][c]
                if not isinstance(entry, tk.Entry):
                    continue
                if str(entry.cget("state")) != "disabled":
                    return False
                if entry.get().strip().upper() != background_grid[r][c]:
                    return False
        return True

    # ===== Letter feedback data =====
    all_puzzle_letters = set()
    for word_info in WORDS_DATA:
        all_puzzle_letters.update(word_info["word"])

    letter_status = {letter: "unused" for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

    def update_keyboard():
        for letter, status in letter_status.items():
            if letter not in letter_labels:
                continue
            if status == "green":
                letter_labels[letter].config(bg="#c8e6c9", fg="black")
            elif status == "yellow":
                letter_labels[letter].config(bg="#fff59d", fg="black")
            elif status == "red":
                letter_labels[letter].config(bg="#ef9a9a", fg="white")

    # ===== Check Letters =====
    def check_letters():
        guesses[0] += 1
        guesses_label.config(text=f"Guesses: {guesses[0]}")

        for r in range(5):
            for c in range(5):
                if background_grid[r][c] is None:
                    continue
                entry = cells[r][c]
                if not isinstance(entry, tk.Entry) or str(entry.cget("state")) == "disabled":
                    continue

                typed = entry.get().strip().upper()
                correct = background_grid[r][c]

                if not typed:
                    continue

                if typed == correct:
                    entry.config(bg="#c8e6c9", state="disabled", disabledbackground="#c8e6c9")
                    letter_status[typed] = "green"
                elif typed in all_puzzle_letters:
                    entry.config(bg="#fff59d")
                    if letter_status[typed] != "green":
                        letter_status[typed] = "yellow"
                else:
                    entry.config(bg="#ef9a9a")
                    if letter_status[typed] not in ("green", "yellow"):
                        letter_status[typed] = "red"

        update_keyboard()

        if is_puzzle_complete():
            status_label.config(
                text=f"Game Complete! Solved in {guesses[0]} guess(es)!",
                fg="#2e7d32"
            )
        else:
            status_label.config(text="")

    # Buttons
    button_frame = tk.Frame(game_frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Check Letters", command=check_letters, font=("Arial", 12)).pack(side="left", padx=5)

    def reveal_all():
        for r in range(5):
            for c in range(5):
                letter = background_grid[r][c]
                if letter and isinstance(cells[r][c], tk.Entry):
                    cells[r][c].config(state="normal")
                    cells[r][c].delete(0, tk.END)
                    cells[r][c].insert(0, letter)
                    cells[r][c].config(bg="#c8e6c9", state="disabled", disabledbackground="#c8e6c9")
                    letter_status[letter] = "green"
        update_keyboard()
        if is_puzzle_complete():
            status_label.config(text="Game Complete! (Revealed)", fg="#2e7d32")

    tk.Button(button_frame, text="Reveal All (Test)", command=reveal_all).pack(side="left", padx=5)

    root.bind("<Return>", lambda e: check_letters())

    # QWERTY Tracker
    keyboard_frame = tk.Frame(game_frame, pady=15)
    keyboard_frame.pack()

    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    letter_labels = {}

    for letters in rows:
        row_frame = tk.Frame(keyboard_frame)
        row_frame.pack()
        for letter in letters:
            lbl = tk.Label(
                row_frame,
                text=letter,
                width=3,
                height=1,
                font=("Arial", 12, "bold"),
                relief="raised",
                borderwidth=1,
                bg="#f0f0f0"
            )
            lbl.pack(side="left", padx=2, pady=2)
            letter_labels[letter] = lbl

    return game_frame


def create_start_screen(root, on_start):
    """Creates the title / start screen."""
    start_frame = tk.Frame(root)

    title = tk.Label(start_frame, text="Word Game", font=("Arial", 32, "bold"))
    title.pack(pady=(80, 20))

    subtitle = tk.Label(start_frame, text="5×5 Crossword Puzzle", font=("Arial", 16))
    subtitle.pack(pady=(0, 40))

    start_btn = tk.Button(
        start_frame,
        text="Start Game",
        font=("Arial", 16),
        width=15,
        height=2,
        command=on_start
    )
    start_btn.pack(pady=20)

    return start_frame


def main():
    root = tk.Tk()
    root.title("Word Game")
    root.geometry("500x700")
    root.resizable(False, False)

    def show_game():
        start_frame.pack_forget()
        game_frame.pack(fill="both", expand=True)

    start_frame = create_start_screen(root, show_game)
    game_frame = create_game(root)

    start_frame.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()