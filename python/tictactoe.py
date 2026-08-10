"""Terminal Tic Tac Toe with an unbeatable alpha-beta AI.

Run with:  python3 tictactoe.py
No third-party dependencies.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from typing import NamedTuple, Optional

EMPTY = " "
X = "X"
O = "O"  # noqa: E741 - the game's mark, not an ambiguous identifier

LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)

EASY, MEDIUM, HARD = "easy", "medium", "hard"
DIFFICULTIES = (EASY, MEDIUM, HARD)

Board = tuple[str, ...]
EMPTY_BOARD: Board = (EMPTY,) * 9


class Outcome(NamedTuple):
    winner: Optional[str]
    line: Optional[tuple[int, int, int]]

    @property
    def is_over(self) -> bool:
        return self.winner is not None


def opponent(player: str) -> str:
    return O if player == X else X


def moves(board: Board) -> tuple[int, ...]:
    return tuple(i for i, cell in enumerate(board) if cell == EMPTY)


def place(board: Board, index: int, player: str) -> Board:
    if board[index] != EMPTY:
        raise ValueError(f"square {index + 1} is already taken")
    cells = list(board)
    cells[index] = player
    return tuple(cells)


def outcome(board: Board) -> Outcome:
    """Winner and winning line, or ("draw", None) once the board is full."""
    for line in LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return Outcome(board[a], line)
    if EMPTY not in board:
        return Outcome("draw", None)
    return Outcome(None, None)


def _score(board: Board, player: str, depth: int, alpha: int, beta: int) -> int:
    """Negamax with alpha-beta pruning, from `player`'s point of view.

    Shallower wins score higher so the AI finishes games instead of stalling.
    """
    result = outcome(board)
    if result.winner == player:
        return 10 - depth
    if result.winner == opponent(player):
        return depth - 10
    if result.winner == "draw":
        return 0

    best = -100
    for move in moves(board):
        value = -_score(place(board, move, player), opponent(player), depth + 1, -beta, -alpha)
        best = max(best, value)
        alpha = max(alpha, value)
        if alpha >= beta:
            break
    return best


def best_move(board: Board, player: str) -> int:
    """The optimal move for `player`, picked at random among equal-value moves."""
    candidates = moves(board)
    if not candidates:
        raise ValueError("no moves available on a full board")

    scored: dict[int, int] = {}
    for move in candidates:
        scored[move] = -_score(place(board, move, player), opponent(player), 1, -100, 100)
    top = max(scored.values())
    return random.choice([m for m, value in scored.items() if value == top])


def _winning_move(board: Board, player: str) -> Optional[int]:
    for move in moves(board):
        if outcome(place(board, move, player)).winner == player:
            return move
    return None


def ai_move(board: Board, player: str, difficulty: str = HARD) -> int:
    """Pick a move for `player`.

    easy   - random.
    medium - takes a win, blocks a loss, otherwise random.
    hard   - perfect play; cannot be beaten.
    """
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"unknown difficulty: {difficulty}")
    candidates = moves(board)
    if not candidates:
        raise ValueError("no moves available on a full board")

    if difficulty == EASY:
        return random.choice(candidates)
    if difficulty == MEDIUM:
        win = _winning_move(board, player)
        if win is not None:
            return win
        block = _winning_move(board, opponent(player))
        if block is not None:
            return block
        return random.choice(candidates)
    return best_move(board, player)


# ---------------------------------------------------------------- rendering


class Palette:
    """ANSI colours, disabled when the output is not a colour-capable tty."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def __call__(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def x(self, text: str) -> str:
        return self(text, "1;36")

    def o(self, text: str) -> str:
        return self(text, "1;35")

    def win(self, text: str) -> str:
        return self(text, "1;30;42")

    def dim(self, text: str) -> str:
        return self(text, "2")

    def bold(self, text: str) -> str:
        return self(text, "1")


def color_support() -> bool:
    return sys.stdout.isatty() and os.environ.get("TERM") != "dumb" and "NO_COLOR" not in os.environ


def render(board: Board, palette: Palette, highlight: tuple[int, ...] = ()) -> str:
    def cell(i: int) -> str:
        mark = board[i]
        text = palette.dim(str(i + 1)) if mark == EMPTY else (palette.x(mark) if mark == X else palette.o(mark))
        return palette.win(f" {mark} ") if i in highlight else f" {text} "

    rows = [f"{cell(r)}│{cell(r + 1)}│{cell(r + 2)}" for r in (0, 3, 6)]
    return "\n" + f"\n{palette.dim('───┼───┼───')}\n".join(rows) + "\n"


def clear_screen() -> None:
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")


# ------------------------------------------------------------------- game


def _read(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        raise KeyboardInterrupt from None


def prompt_move(board: Board, player: str, palette: Palette) -> int:
    mark = palette.x(player) if player == X else palette.o(player)
    while True:
        answer = _read(f"{mark} pick a square (1-9, q to quit): ").lower()
        if answer in ("q", "quit", "exit"):
            raise KeyboardInterrupt
        if not answer.isdigit() or not 1 <= int(answer) <= 9:
            print(palette.dim("  enter a number from 1 to 9"))
            continue
        index = int(answer) - 1
        if board[index] != EMPTY:
            print(palette.dim("  that square is taken"))
            continue
        return index


def prompt_choice(question: str, options: dict[str, str], palette: Palette) -> str:
    keys = "/".join(options)
    while True:
        answer = _read(f"{question} [{keys}]: ").lower()
        if answer in options:
            return options[answer]
        print(palette.dim(f"  choose one of: {keys}"))


def play_round(vs_ai: bool, difficulty: str, human: str, palette: Palette) -> Optional[str]:
    """Play one round; returns X, O or "draw"."""
    board = EMPTY_BOARD
    current = X
    while True:
        clear_screen()
        print(palette.bold("  Tic Tac Toe"))
        print(render(board, palette))
        result = outcome(board)
        if result.is_over:
            clear_screen()
            print(palette.bold("  Tic Tac Toe"))
            print(render(board, palette, result.line or ()))
            return result.winner

        if vs_ai and current != human:
            move = ai_move(board, current, difficulty)
            print(palette.dim(f"AI plays {move + 1}"))
        else:
            move = prompt_move(board, current, palette)
        board = place(board, move, current)
        current = opponent(current)


def scoreboard(scores: dict[str, int], palette: Palette) -> str:
    return palette.bold(
        f"  {palette.x('X')} {scores[X]}   {palette.o('O')} {scores[O]}   draws {scores['draw']}"
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Terminal Tic Tac Toe with an unbeatable AI.")
    parser.add_argument("--mode", choices=("ai", "pvp"), help="skip the menu and start this mode")
    parser.add_argument("--difficulty", choices=DIFFICULTIES, default=HARD, help="AI strength (default: hard)")
    parser.add_argument("--mark", choices=(X, O), default=X, help="your mark against the AI; X moves first")
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colours")
    args = parser.parse_args(argv)

    palette = Palette(color_support() and not args.no_color)
    scores = {X: 0, O: 0, "draw": 0}

    try:
        vs_ai = args.mode != "pvp" if args.mode else (
            prompt_choice("Play against the (a)i or a (p)layer?", {"a": "ai", "p": "pvp"}, palette) == "ai"
        )
        difficulty = args.difficulty
        if vs_ai and not args.mode:
            difficulty = prompt_choice(
                "Difficulty", {"e": EASY, "m": MEDIUM, "h": HARD}, palette
            )

        while True:
            winner = play_round(vs_ai, difficulty, args.mark, palette)
            scores[winner] += 1
            if winner == "draw":
                print("  Draw.")
            elif vs_ai:
                print("  You win!" if winner == args.mark else "  The AI wins.")
            else:
                print(f"  {winner} wins!")
            print(scoreboard(scores, palette))
            if prompt_choice("Play again?", {"y": "y", "n": "n"}, palette) == "n":
                break
    except KeyboardInterrupt:
        print()

    print(palette.dim("  Thanks for playing."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
