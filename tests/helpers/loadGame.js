const path = require("path");

const GAME_PATH = path.join(__dirname, "..", "..", "game.js");

// The game reads #menu/#game/#board/#status at load time, so the DOM must
// exist before the module is required.
const DOM = `
  <div class="menu" id="menu"><div class="menu-box"></div></div>
  <div class="game-box" id="game">
    <div class="status" id="status"></div>
    <div class="board" id="board"></div>
  </div>
`;

function loadGame() {
  document.body.innerHTML = DOM;
  let mod;
  jest.isolateModules(() => {
    mod = require(GAME_PATH);
  });
  return mod;
}

function cells() {
  return Array.from(document.querySelectorAll(".cell"));
}

function play(game, ...indices) {
  for (const i of indices) {
    cells()[i].click();
  }
}

function boardText() {
  return cells().map((cell) => cell.textContent);
}

function status() {
  return document.getElementById("status").textContent;
}

module.exports = { loadGame, cells, play, boardText, status, GAME_PATH };
