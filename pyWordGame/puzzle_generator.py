import random
import os

def load_words(filepath="words.txt"):
    """Load the 5-letter word list (looks next to this script)."""
    # Get the folder where this .py file lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)
    
    with open(full_path, "r") as f:
        words = [line.strip().lower() for line in f if len(line.strip()) == 5]
    return words

def generate_puzzle(words, max_attempts=200):
    """
    Generate a 3-word 5x5 crossword following your rules:
    - Pick a random center word (horizontal or vertical)
    - Cross a second word on a random letter of the first
    - Cross a third word on a different letter of the first
    """
    words = [w.upper() for w in words]
    word_set = set(words)

    for attempt in range(max_attempts):
        # --- Word 1: center ---
        word1 = random.choice(words)
        horizontal = random.choice([True, False])

        if horizontal:
            # Middle row (row 3, 1-indexed)
            positions1 = [[3, c] for c in range(1, 6)]
        else:
            # Middle column (col 3)
            positions1 = [[r, 3] for r in range(1, 6)]

        placed = {tuple(pos): word1[i] for i, pos in enumerate(positions1)}
        used_intersections = set()

        # Helper to try placing a crossing word
        def try_place_crossing(base_word, base_positions, used):
            # Pick a random letter position that hasn't been used yet
            available = [i for i in range(5) if i not in used]
            if not available:
                return None
            idx = random.choice(available)
            letter = base_word[idx]
            cross_pos = base_positions[idx]  # [row, col]

            # Crossing direction is opposite of the base word
            cross_horizontal = not horizontal if base_word is word1 else horizontal

            # Try every possible offset for the crossing word
            candidates = []
            for offset in range(5):
                if cross_horizontal:
                    # Horizontal crossing word
                    start_col = cross_pos[1] - offset
                    if start_col < 1 or start_col + 4 > 5:
                        continue
                    positions = [[cross_pos[0], start_col + i] for i in range(5)]
                else:
                    # Vertical crossing word
                    start_row = cross_pos[0] - offset
                    if start_row < 1 or start_row + 4 > 5:
                        continue
                    positions = [[start_row + i, cross_pos[1]] for i in range(5)]

                # Build the required letter pattern
                pattern = [None] * 5
                conflict = False
                for i, pos in enumerate(positions):
                    tpos = tuple(pos)
                    if tpos in placed:
                        if placed[tpos] != None and i != offset:
                            # Only the intersection letter is allowed to already exist
                            # (and it must match)
                            if placed[tpos] != letter:
                                conflict = True
                                break
                        pattern[i] = placed[tpos]
                    else:
                        pattern[i] = None

                if conflict or pattern[offset] not in (None, letter):
                    continue

                # Find words that match the pattern
                for w in words:
                    if all(pattern[i] is None or w[i] == pattern[i] for i in range(5)):
                        if w[offset] == letter:
                            candidates.append((w, positions, idx))

            if not candidates:
                return None

            word, positions, used_idx = random.choice(candidates)
            return word, positions, used_idx

        # --- Word 2 ---
        result2 = try_place_crossing(word1, positions1, used_intersections)
        if not result2:
            continue
        word2, positions2, used_idx2 = result2
        used_intersections.add(used_idx2)
        for i, pos in enumerate(positions2):
            placed[tuple(pos)] = word2[i]

        # --- Word 3 (must use a different intersection letter) ---
        result3 = try_place_crossing(word1, positions1, used_intersections)
        if not result3:
            continue
        word3, positions3, used_idx3 = result3
        for i, pos in enumerate(positions3):
            placed[tuple(pos)] = word3[i]

        # Success — return in the format the game expects
        return [
            {"word": word1, "positions": positions1},
            {"word": word2, "positions": positions2},
            {"word": word3, "positions": positions3},
        ]

    # Fallback if we couldn't generate one
    return None


# Quick test
if __name__ == "__main__":
    words = load_words()
    puzzle = generate_puzzle(words)
    if puzzle:
        for p in puzzle:
            print(p["word"], p["positions"])
    else:
        print("Failed to generate a puzzle")