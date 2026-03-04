export const DEFAULT_GRID_SIZE = 16;

export const DIRECTIONS = {
  UP: { x: 0, y: -1 },
  DOWN: { x: 0, y: 1 },
  LEFT: { x: -1, y: 0 },
  RIGHT: { x: 1, y: 0 }
};

export function createInitialState(gridSize = DEFAULT_GRID_SIZE) {
  const startX = Math.floor(gridSize / 2);
  const startY = Math.floor(gridSize / 2);

  const snake = [
    { x: startX, y: startY },
    { x: startX - 1, y: startY },
    { x: startX - 2, y: startY }
  ];

  return {
    gridSize,
    snake,
    direction: DIRECTIONS.RIGHT,
    pendingDirection: DIRECTIONS.RIGHT,
    food: findNextFoodPosition(gridSize, snake),
    score: 0,
    gameOver: false,
    paused: false
  };
}

export function setDirection(state, nextDirection) {
  if (state.gameOver) {
    return state;
  }

  if (isOppositeDirection(state.direction, nextDirection)) {
    return state;
  }

  return {
    ...state,
    pendingDirection: nextDirection
  };
}

export function togglePause(state) {
  if (state.gameOver) {
    return state;
  }

  return {
    ...state,
    paused: !state.paused
  };
}

export function getGameStatus(state) {
  if (state.gameOver) {
    return 'Game over';
  }

  if (state.paused) {
    return 'Paused';
  }

  return 'Running';
}

export function stepGame(state) {
  if (state.gameOver || state.paused) {
    return state;
  }

  const direction = state.pendingDirection;
  const head = state.snake[0];
  const nextHead = {
    x: head.x + direction.x,
    y: head.y + direction.y
  };

  if (isOutOfBounds(nextHead, state.gridSize)) {
    return {
      ...state,
      direction,
      gameOver: true
    };
  }

  const willGrow = positionsEqual(nextHead, state.food);
  const bodyForCollision = willGrow ? state.snake : state.snake.slice(0, -1);

  if (containsPosition(bodyForCollision, nextHead)) {
    return {
      ...state,
      direction,
      gameOver: true
    };
  }

  const nextSnake = [nextHead, ...state.snake];
  if (!willGrow) {
    nextSnake.pop();
  }

  return {
    ...state,
    snake: nextSnake,
    direction,
    pendingDirection: direction,
    food: willGrow ? findNextFoodPosition(state.gridSize, nextSnake) : state.food,
    score: willGrow ? state.score + 1 : state.score
  };
}

export function findNextFoodPosition(gridSize, snake) {
  for (let y = 0; y < gridSize; y += 1) {
    for (let x = 0; x < gridSize; x += 1) {
      const candidate = { x, y };
      if (!containsPosition(snake, candidate)) {
        return candidate;
      }
    }
  }

  return null;
}

export function containsPosition(positions, target) {
  return positions.some((pos) => positionsEqual(pos, target));
}

export function positionsEqual(a, b) {
  return a && b && a.x === b.x && a.y === b.y;
}

export function isOutOfBounds(position, gridSize) {
  return (
    position.x < 0 ||
    position.y < 0 ||
    position.x >= gridSize ||
    position.y >= gridSize
  );
}

function isOppositeDirection(currentDirection, nextDirection) {
  return (
    currentDirection.x + nextDirection.x === 0 &&
    currentDirection.y + nextDirection.y === 0
  );
}
