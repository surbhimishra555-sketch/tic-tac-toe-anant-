module.exports = {
  testEnvironment: "jsdom",
  collectCoverageFrom: ["game.js"],
  coverageThreshold: {
    global: { statements: 90, branches: 85, functions: 90, lines: 90 },
  },
};
