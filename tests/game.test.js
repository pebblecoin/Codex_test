import test from 'node:test';
import assert from 'node:assert/strict';
import {
  DIRECTIONS,
  createInitialState,
  findNextFoodPosition,
  getGameStatus,
  setDirection,
  stepGame,
  togglePause
} from '../src/game.js';

test('snake moves one step in current direction', () => {
  const start = createInitialState(8);
  const next = stepGame(start);

  assert.deepEqual(next.snake[0], {
    x: start.snake[0].x + 1,
    y: start.snake[0].y
  });
  assert.equal(next.snake.length, start.snake.length);
  assert.equal(next.score, 0);
});

test('snake grows and score increments when eating food', () => {
  const start = createInitialState(8);
  const head = start.snake[0];
  const state = {
    ...start,
    food: { x: head.x + 1, y: head.y }
  };

  const next = stepGame(state);

  assert.equal(next.snake.length, state.snake.length + 1);
  assert.equal(next.score, 1);
});

test('wall collision ends game', () => {
  const state = {
    ...createInitialState(4),
    snake: [
      { x: 3, y: 1 },
      { x: 2, y: 1 },
      { x: 1, y: 1 }
    ],
    direction: DIRECTIONS.RIGHT,
    pendingDirection: DIRECTIONS.RIGHT
  };

  const next = stepGame(state);
  assert.equal(next.gameOver, true);
});

test('self collision ends game', () => {
  const state = {
    ...createInitialState(6),
    snake: [
      { x: 2, y: 2 },
      { x: 2, y: 3 },
      { x: 3, y: 3 },
      { x: 3, y: 2 }
    ],
    direction: DIRECTIONS.RIGHT,
    pendingDirection: DIRECTIONS.DOWN,
    food: { x: 0, y: 0 }
  };

  const next = stepGame(state);
  assert.equal(next.gameOver, true);
});

test('cannot reverse direction in a single move', () => {
  const start = createInitialState(8);
  const updated = setDirection(start, DIRECTIONS.LEFT);

  assert.deepEqual(updated.pendingDirection, DIRECTIONS.RIGHT);
});

test('food placement picks first free tile deterministically', () => {
  const snake = [
    { x: 0, y: 0 },
    { x: 1, y: 0 },
    { x: 2, y: 0 }
  ];

  const food = findNextFoodPosition(4, snake);
  assert.deepEqual(food, { x: 3, y: 0 });
});

test('pause blocks movement until resumed', () => {
  const start = createInitialState(8);
  const paused = togglePause(start);
  const whilePaused = stepGame(paused);
  const resumed = togglePause(whilePaused);
  const afterResume = stepGame(resumed);

  assert.equal(paused.paused, true);
  assert.equal(whilePaused, paused);
  assert.notEqual(afterResume, resumed);
  assert.deepEqual(afterResume.snake[0], {
    x: start.snake[0].x + 1,
    y: start.snake[0].y
  });
});

test('setDirection is a no-op after game over', () => {
  const state = {
    ...createInitialState(8),
    gameOver: true
  };

  const updated = setDirection(state, DIRECTIONS.UP);
  assert.equal(updated, state);
});

test('stepGame is a no-op after game over', () => {
  const state = {
    ...createInitialState(8),
    gameOver: true
  };

  const next = stepGame(state);
  assert.equal(next, state);
});

test('moving into vacated tail cell is allowed when not growing', () => {
  const state = {
    ...createInitialState(5),
    snake: [
      { x: 2, y: 2 },
      { x: 2, y: 1 },
      { x: 1, y: 1 },
      { x: 1, y: 2 }
    ],
    direction: DIRECTIONS.RIGHT,
    pendingDirection: DIRECTIONS.LEFT,
    food: { x: 4, y: 4 }
  };

  const next = stepGame(state);

  assert.equal(next.gameOver, false);
  assert.deepEqual(next.snake[0], { x: 1, y: 2 });
  assert.equal(next.snake.length, state.snake.length);
});

test('food placement returns null when grid is full', () => {
  const snake = [
    { x: 0, y: 0 },
    { x: 1, y: 0 },
    { x: 0, y: 1 },
    { x: 1, y: 1 }
  ];

  const food = findNextFoodPosition(2, snake);
  assert.equal(food, null);
});

test('getGameStatus reports running, paused, and game over in order', () => {
  const start = createInitialState(8);
  const paused = togglePause(start);
  const ended = { ...paused, gameOver: true };

  assert.equal(getGameStatus(start), 'Running');
  assert.equal(getGameStatus(paused), 'Paused');
  assert.equal(getGameStatus(ended), 'Game over');
});
