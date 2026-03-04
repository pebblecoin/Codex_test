import {
  DEFAULT_GRID_SIZE,
  DIRECTIONS,
  containsPosition,
  createInitialState,
  getGameStatus,
  setDirection,
  stepGame,
  togglePause
} from './game.js';

const TICK_MS = 150;

const boardEl = document.getElementById('board');
const scoreEl = document.getElementById('score');
const statusEl = document.getElementById('status');
const restartBtn = document.getElementById('restartBtn');
const pauseBtn = document.getElementById('pauseBtn');
const touchButtons = document.querySelectorAll('[data-dir]');

let state = createInitialState(DEFAULT_GRID_SIZE);

function restartGame() {
  state = createInitialState(DEFAULT_GRID_SIZE);
  render();
}

function onDirectionInput(dirKey) {
  const direction = DIRECTIONS[dirKey];
  if (!direction) {
    return;
  }
  state = setDirection(state, direction);
}

function handleKeyDown(event) {
  const keyMap = {
    ArrowUp: 'UP',
    ArrowDown: 'DOWN',
    ArrowLeft: 'LEFT',
    ArrowRight: 'RIGHT',
    w: 'UP',
    W: 'UP',
    s: 'DOWN',
    S: 'DOWN',
    a: 'LEFT',
    A: 'LEFT',
    d: 'RIGHT',
    D: 'RIGHT'
  };

  if (event.code === 'Space') {
    event.preventDefault();
    state = togglePause(state);
    render();
    return;
  }

  const mapped = keyMap[event.key];
  if (!mapped) {
    return;
  }

  event.preventDefault();
  onDirectionInput(mapped);
}

function render() {
  const cellCount = state.gridSize * state.gridSize;
  boardEl.innerHTML = '';
  boardEl.style.gridTemplateColumns = `repeat(${state.gridSize}, 1fr)`;

  for (let i = 0; i < cellCount; i += 1) {
    const x = i % state.gridSize;
    const y = Math.floor(i / state.gridSize);
    const cell = document.createElement('div');
    cell.className = 'cell';

    if (containsPosition(state.snake, { x, y })) {
      cell.classList.add('snake');
    } else if (state.food && state.food.x === x && state.food.y === y) {
      cell.classList.add('food');
    }

    boardEl.appendChild(cell);
  }

  scoreEl.textContent = String(state.score);

  statusEl.textContent = getGameStatus(state);

  pauseBtn.textContent = state.paused ? 'Resume' : 'Pause';
}

function tick() {
  state = stepGame(state);
  render();
}

document.addEventListener('keydown', handleKeyDown);
restartBtn.addEventListener('click', restartGame);
pauseBtn.addEventListener('click', () => {
  state = togglePause(state);
  render();
});
touchButtons.forEach((button) => {
  button.addEventListener('click', () => {
    onDirectionInput(button.dataset.dir);
  });
});

render();
setInterval(tick, TICK_MS);
