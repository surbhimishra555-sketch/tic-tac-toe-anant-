const { loadGame, cells, play, boardText, status } = require("./helpers/loadGame");

const PLAYER = "😈";
const AI = "😇";

describe("mode selection / visibility", () => {
  test("startPvP hides the menu, shows the board and builds 9 cells", () => {
    const game = loadGame();
    game.startPvP();
    expect(document.getElementById("menu").style.display).toBe("none");
    expect(document.getElementById("game").style.display).toBe("block");
    expect(cells()).toHaveLength(9);
  });

  test("startAI also reveals the board", () => {
    const game = loadGame();
    game.startAI();
    expect(document.getElementById("game").style.display).toBe("block");
    expect(cells()).toHaveLength(9);
  });
});

describe("init / restart", () => {
  test("init sets the starting player and empty board", () => {
    const game = loadGame();
    game.startPvP();
    expect(status()).toBe(`Player ${PLAYER} turn`);
    expect(boardText().every((t) => t === "")).toBe(true);
    expect(game.getState().every((s) => s === "")).toBe(true);
  });

  test("restartGame clears a dirtied board", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0, 1);
    game.restartGame();
    expect(boardText().every((t) => t === "")).toBe(true);
    expect(status()).toBe(`Player ${PLAYER} turn`);
  });
});

describe("makeMove (Player vs Player)", () => {
  test("first move places the PLAYER symbol", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 4);
    expect(boardText()[4]).toBe(PLAYER);
    expect(game.getState()[4]).toBe(PLAYER);
  });

  test("turns alternate between the two symbols", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0, 1);
    expect(boardText()[0]).toBe(PLAYER);
    expect(boardText()[1]).toBe(AI);
    expect(status()).toBe(`Player ${PLAYER} turn`);
  });

  test("clicking an occupied cell is ignored", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0); // PLAYER
    play(game, 0); // ignored
    expect(boardText()[0]).toBe(PLAYER);
    expect(status()).toBe(`Player ${AI} turn`);
  });

  test("moves are ignored once the game is over", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0, 3, 1, 4, 2); // PLAYER wins top row
    expect(status()).toBe(`${PLAYER} wins 🎉`);
    play(game, 5);
    expect(boardText()[5]).toBe("");
  });
});

describe("checkWin (win + highlight)", () => {
  test("a completed row is a win and the cells get the 'win' class", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0, 3, 1, 4, 2);
    expect(status()).toBe(`${PLAYER} wins 🎉`);
    const c = cells();
    expect(c[0].classList.contains("win")).toBe(true);
    expect(c[1].classList.contains("win")).toBe(true);
    expect(c[2].classList.contains("win")).toBe(true);
  });

  test("a diagonal win is detected", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0, 1, 4, 2, 8);
    expect(status()).toBe(`${PLAYER} wins 🎉`);
  });

  test("checkWin returns false with no complete line", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0);
    expect(game.checkWin(PLAYER)).toBe(false);
  });
});

describe("draw detection", () => {
  test("a full board with no winner reports a draw", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0, 1, 2, 4, 3, 5, 7, 6, 8);
    expect(status()).toBe("Draw 😐");
  });
});

describe("checkWinner (pure, no DOM side effects)", () => {
  test("true for the winner, false for the loser", () => {
    const game = loadGame();
    game.startPvP();
    const s = game.getState();
    s[0] = AI; s[1] = AI; s[2] = AI;
    expect(game.checkWinner(AI)).toBe(true);
    expect(game.checkWinner(PLAYER)).toBe(false);
    // checkWinner must not add the 'win' class (unlike checkWin)
    expect(cells()[0].classList.contains("win")).toBe(false);
  });
});

describe("minimax", () => {
  test("scores a win the maximizer (AI) can reach as 10 - depth", () => {
    const game = loadGame();
    game.startAI();
    const s = game.getState();
    s[0] = AI; s[1] = AI; // AI can complete 0,1,2 one ply deep
    expect(game.minimax(s, 0, true)).toBe(9); // 10 - depth(1)
  });

  test("scores a line the minimizer (PLAYER) can win as depth - 10", () => {
    const game = loadGame();
    game.startAI();
    const s = game.getState();
    s[3] = PLAYER; s[4] = PLAYER; // PLAYER can complete 3,4,5 next move
    // Minimizer to move wins one ply deep -> depth(1) - 10 = -9
    expect(game.minimax(s, 0, false)).toBe(-9);
  });

  test("returns 0 for a full drawn board", () => {
    const game = loadGame();
    game.startAI();
    const draw = [PLAYER, AI, PLAYER, PLAYER, AI, AI, AI, PLAYER, PLAYER];
    expect(game.minimax(draw, 0, true)).toBe(0);
  });
});

describe("aiMove (driven through a real AI turn)", () => {
  test("takes the immediately winning move", () => {
    jest.useFakeTimers();
    const game = loadGame();
    game.startAI();
    const s = game.getState();
    s[0] = AI; s[1] = AI; // AI can complete 0,1,2
    play(game, 8); // player moves -> AI turn is scheduled
    jest.runOnlyPendingTimers();
    expect(game.getState()[2]).toBe(AI);
    expect(status()).toBe(`${AI} wins 🎉`);
    jest.useRealTimers();
  });

  test("blocks the player's immediate winning threat", () => {
    jest.useFakeTimers();
    const game = loadGame();
    game.startAI();
    game.getState()[0] = PLAYER; // player already holds a corner
    play(game, 1); // player now threatens 0,1,2 -> AI turn scheduled
    jest.runOnlyPendingTimers();
    expect(game.getState()[2]).toBe(AI); // AI must block at 2
    jest.useRealTimers();
  });

  test("is a no-op after the game is over", () => {
    const game = loadGame();
    game.startPvP();
    play(game, 0, 3, 1, 4, 2); // PLAYER wins -> active = false
    const before = boardText();
    game.aiMove();
    expect(boardText()).toEqual(before);
  });
});

describe("AI turn scheduling", () => {
  test("after a player move the AI responds on the timer", () => {
    jest.useFakeTimers();
    const game = loadGame();
    game.startAI();
    play(game, 0);
    expect(status()).toBe("AI thinking 🤖...");
    expect(boardText().filter((t) => t === AI)).toHaveLength(0);
    jest.runOnlyPendingTimers();
    expect(boardText().filter((t) => t === AI)).toHaveLength(1);
    expect(boardText()[0]).toBe(PLAYER);
    jest.useRealTimers();
  });
});
