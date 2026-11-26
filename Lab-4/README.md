# Lab 4 – Vibe Coding: Real-Time Flappy Bird Clone

**Name:** Rhea Menon
**SRN:** PES1UG24AM222
**Assigned repo:** [SETAPESU26/40_flappy-bird](https://github.com/SETAPESU26/40_flappy-bird)
**LLM used:** Claude

A Pygame Flappy Bird clone. The starter code was only partly working, so I used an LLM as a pair programmer to fix the bugs and add all the features listed in the original README. Each task is its own commit.

## Deliverables

| Item | File / link |
| --- | --- |
| Video **before** the changes (10 s) | `videos/before.mp4` |
| Video **after** the changes (10 s) | `videos/after.mp4` |
| Updated code | `main.py`, `game/` |
| Chat history (exported) | `chat_history.pdf` |

## How to run

```bash
pip install -r requirements.txt
python main.py
```

**Controls**

| Key / mouse | Action |
| --- | --- |
| `Space` or left-click | Flap (the first flap starts the round) |
| `1` / `E`, `2` / `M`, `3` / `H` | On Game Over: play again on Easy / Medium / Hard |
| `Space` / `Enter` | On Game Over: replay on the same difficulty |
| `Esc` / `Q` | On Game Over: quit |

The difficulty and Quit buttons on the Game Over screen can also be clicked.

## What was changed

### Task 1 – Refine collision detection (bug fix)
**Problem:** collision only tested the bird's single *centre point* against the pipe rectangles, so the bird could visibly overlap a pipe's edge or corner and survive. This got worse as pipe speed increased.
**Fix:** `Pipe.collides_with_circle()` does exact circle-vs-rectangle maths (closest point on the rectangle to the bird's centre, compared with the radius). The engine also splits each frame's movement into sub-steps of at most 2 px. Because of this, a fast pipe or a fast fall can't jump past an edge between frames.

### Task 2 – Game Over screen
Replaced the `print("Game over! ...")` to the console with an on-screen Game Over panel showing the final score. The game freezes behind a dimmed overlay and waits for input. Input is ignored for ~0.5 s after dying so a late flap doesn't skip the screen.

### Task 3 – Replay with difficulty
The Game Over screen offers **Easy / Medium / Hard** or **Quit**:

| Difficulty | Pipe speed | Gap | Spawn interval |
| --- | --- | --- | --- |
| Easy | 3 px/frame | 190 px | 110 frames |
| Medium (original) | 4 px/frame | 150 px | 90 frames |
| Hard | 6 px/frame | 120 px | 70 frames |

The current difficulty is shown in the top-right corner during play.

### Task 4 – Sound feedback
`game/sounds.py` makes three short 8-bit style sound effects in code, so the game needs no audio files:
- **Flap:** a short rising chirp
- **Score** (passing a pipe): a two-note ding
- **Death:** a falling buzz, played once

If the computer has no audio device, the game runs silently instead of crashing.

### Extra fix – bird died before the player could react
In the original game the round started the moment the window opened. The bird hit the ground in about 0.6 s, often before the window even had keyboard focus. The game now shows a **"Get Ready"** screen with the bird hovering in place. Gravity and pipes start only on the first flap, including after every replay.

## Commits

1. Add Flappy Bird starter code (unchanged)
2. Task 1: fix pipe collision detection
3. Task 2: add Game Over screen
4. Task 3: add replay with difficulty selection
5. Task 4: add sound effects for flap, score and death
6. Fix bird dying before the player can react (Get Ready screen)

## Folder structure

```
Lab-4/
├── main.py
├── requirements.txt
├── README.md
├── game/
│   ├── game_engine.py   # game loop logic, collision, Game Over + replay menu
│   ├── bird.py
│   ├── pipe.py          # + circle-vs-rect collision
│   └── sounds.py        # new: synthesised sound effects
├── videos/
│   ├── before.mp4
│   └── after.mp4
└── chat_history.pdf
```
