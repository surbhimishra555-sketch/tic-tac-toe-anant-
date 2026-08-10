# Terminal Tic Tac Toe (Python)

A colourful terminal version of the game, with an AI that cannot be beaten.
Pure standard library — Python 3.9+, no installs.

```bash
python3 python/tictactoe.py
```

```
  Tic Tac Toe

 X │ X │ O
───┼───┼───
 4 │ O │ 6
───┼───┼───
 7 │ 8 │ 9

X pick a square (1-9, q to quit):
```

Squares are numbered like a phone keypad: `1`–`9`, left to right, top to bottom.
Press `q` at any prompt to quit.

## Options

| Flag | Meaning |
|------|---------|
| `--mode ai\|pvp` | skip the menu and start that mode |
| `--difficulty easy\|medium\|hard` | AI strength (default `hard`) |
| `--mark X\|O` | your mark against the AI; `X` always moves first |
| `--no-color` | plain output (also honours `NO_COLOR` and non-tty pipes) |

```bash
python3 python/tictactoe.py --mode ai --difficulty medium --mark O
```

## Difficulties

- **easy** — random moves.
- **medium** — takes a win, blocks a loss, otherwise random.
- **hard** — negamax with alpha-beta pruning over the full game tree. Perfect play: the
  best you can get is a draw. Equally-good moves are chosen at random so games vary.

## Tests

```bash
cd python && python3 -m unittest -v
```

The suite includes an exhaustive check that plays the hard AI against *every* possible
sequence of opponent moves and asserts it never loses.
