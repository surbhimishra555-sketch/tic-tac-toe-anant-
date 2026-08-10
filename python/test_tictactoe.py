import random
import unittest

from tictactoe import (
    EASY,
    EMPTY,
    EMPTY_BOARD,
    HARD,
    MEDIUM,
    O,
    X,
    Palette,
    ai_move,
    best_move,
    moves,
    opponent,
    outcome,
    place,
    render,
)


def board(cells: str):
    """Build a board from a 9 character string, '.' meaning empty."""
    assert len(cells) == 9
    return tuple(EMPTY if c == "." else c for c in cells)


class RulesTest(unittest.TestCase):
    def test_empty_board_is_undecided(self):
        self.assertEqual(outcome(EMPTY_BOARD), (None, None))

    def test_detects_row_column_and_diagonal(self):
        self.assertEqual(outcome(board("XXX...OO.")).winner, X)
        self.assertEqual(outcome(board("O.XO.XO..")).winner, O)
        self.assertEqual(outcome(board("X.O.XO..X")).winner, X)
        self.assertEqual(outcome(board("XXX...OO.")).line, (0, 1, 2))

    def test_full_board_without_a_line_is_a_draw(self):
        self.assertEqual(outcome(board("XXOOOXXOX")).winner, "draw")

    def test_place_rejects_taken_squares(self):
        with self.assertRaises(ValueError):
            place(board("X........"), 0, O)

    def test_place_does_not_mutate_the_original(self):
        start = EMPTY_BOARD
        place(start, 4, X)
        self.assertEqual(start, EMPTY_BOARD)

    def test_opponent(self):
        self.assertEqual(opponent(X), O)
        self.assertEqual(opponent(O), X)


class AITest(unittest.TestCase):
    def test_takes_the_immediate_win(self):
        self.assertEqual(best_move(board("XX.OO...."), X), 2)

    def test_blocks_the_opponent(self):
        self.assertEqual(best_move(board("OO.X..X.."), X), 2)

    def test_prefers_the_faster_win(self):
        # X can win now at 2; taking it must beat any slower line.
        self.assertEqual(best_move(board("XX.OO..X."), X), 2)

    def test_medium_wins_then_blocks(self):
        self.assertEqual(ai_move(board("XX.OO...."), X, MEDIUM), 2)
        self.assertEqual(ai_move(board("OO.X..X.."), X, MEDIUM), 2)

    def test_easy_stays_on_the_board(self):
        random.seed(0)
        state = board("XX.OO....")
        self.assertIn(ai_move(state, X, EASY), moves(state))

    def test_unknown_difficulty_is_rejected(self):
        with self.assertRaises(ValueError):
            ai_move(EMPTY_BOARD, X, "impossible")

    def test_full_board_has_no_move(self):
        with self.assertRaises(ValueError):
            ai_move(board("XXOOOXXOX"), X, HARD)

    def test_hard_ai_never_loses(self):
        """Perfect AI as O against every possible line of play by X."""

        def walk(state, turn):
            result = outcome(state)
            if result.is_over:
                self.assertNotEqual(result.winner, X, f"AI lost on {state}")
                return
            if turn == O:
                walk(place(state, ai_move(state, O, HARD), O), X)
                return
            for move in moves(state):
                walk(place(state, move, X), O)

        random.seed(0)
        walk(EMPTY_BOARD, X)


class RenderTest(unittest.TestCase):
    def test_plain_render_shows_marks_and_hints(self):
        plain = render(board("X...O...."), Palette(enabled=False))
        self.assertIn("X", plain)
        self.assertIn("O", plain)
        self.assertIn("2", plain)  # empty squares are numbered
        self.assertNotIn("\033", plain)

    def test_colour_render_is_escaped(self):
        self.assertIn("\033", render(board("X........"), Palette(enabled=True)))


if __name__ == "__main__":
    unittest.main()
