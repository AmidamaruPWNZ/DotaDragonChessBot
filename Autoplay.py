import cv2
import numpy as np
import pyautogui
import time
import keyboard

# Загрузка эталонных изображений блоков
TEMPLATES = {
    'Y': cv2.imread('Samples/yellow.png'),  # Crystal Maiden
    'B': cv2.imread('Samples/blue.png'),    # Lich
    'P': cv2.imread('Samples/purple.png'),  # Vengeful Spirit
    'R': cv2.imread('Samples/red.png'),     # Lina
    'L_B': cv2.imread('Samples/L_blue.png'),  # Winter Wyvern
    'D_R': cv2.imread('Samples/D_red.png'),  # Brood Mother
}

# Размер блока
BLOCK_SIZE = 94

# Положение и размер игрового окна (x, y, width, height)
GAME_REGION = (208, 117, 750, 750)

# Флаг для остановки скрипта
running = True


# Функция для остановки скрипта при нажатии 'q'
def stop_script(e):
    global running
    running = False


keyboard.on_press_key('q', stop_script)


def capture_screen(region):
    """Захватывает скриншот игровой области."""
    screenshot = pyautogui.screenshot(region=region)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return frame


def find_blocks(frame, templates, threshold=0.7):
    """Находит блоки на экране и возвращает их координаты и тип."""
    blocks = []
    for label, template in templates.items():
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        for pt in zip(*locations[::-1]):
            x, y = pt
            blocks.append((label, x, y))
    return blocks


def check_possible_moves(blocks):
    """Проверка возможных ходов для 'три в ряд' и более."""
    moves = []
    grid = {}
    for label, x, y in blocks:
        grid_x = round(x / BLOCK_SIZE)
        grid_y = round(y / BLOCK_SIZE)
        grid[(grid_x, grid_y)] = label

    directions = [(0, 1), (1, 0)]  # Проверка вправо и вниз
    for (i, j), label in grid.items():
        for dx, dy in directions:
            # Проверка соседнего блока
            ni, nj = i + dx, j + dy
            if (ni, nj) not in grid:
                continue

            # Поменять блоки местами
            grid[(i, j)], grid[(ni, nj)] = grid[(ni, nj)], grid[(i, j)]

            # Проверить совпадения
            if is_match(grid, i, j) or is_match(grid, ni, nj):
                moves.append(((i, j), (ni, nj)))

            # Вернуть блоки на место
            grid[(i, j)], grid[(ni, nj)] = grid[(ni, nj)], grid[(i, j)]

    return moves


def is_match(grid, i, j):
    """Проверка, образуется ли три в ряд или больше после перемещения."""
    label = grid.get((i, j))
    if not label:
        return False

    # Проверка по горизонтали на 3 и более одинаковых блоков
    horizontal = [grid.get((i + offset, j)) == label for offset in range(-2, 3)]
    if check_consecutive_n(horizontal, 3):
        return True

    # Проверка по вертикали на 3 и более одинаковых блоков
    vertical = [grid.get((i, j + offset)) == label for offset in range(-2, 3)]
    if check_consecutive_n(vertical, 3):
        return True

    return False


def check_consecutive_n(line, n):
    """Проверяет, есть ли n подряд True в списке."""
    count = 0
    for value in line:
        if value:
            count += 1
            if count >= n:
                return True
        else:
            count = 0
    return False


def move_and_drag(start_x, start_y, dx, dy):
    """Перемещает блок в указанном направлении, если это действительно необходимо."""
    # Проверяем, нужно ли вообще двигать блок
    if dx == 0 and dy == 0:
        print("Нет нужды перемещать блок.")
        return

    end_x = start_x + dx
    end_y = start_y + dy
    pyautogui.moveTo(start_x, start_y, duration=0.16)
    pyautogui.mouseDown(duration=0.05)
    pyautogui.moveTo(end_x, end_y, duration=0.16)
    pyautogui.mouseUp(duration=0.05)
    print(f"Перемещение с ({start_x}, {start_y}) на ({end_x}, {end_y})")


# Основной цикл игры
time.sleep(2)  # Задержка перед стартом
while running:
    frame = capture_screen(GAME_REGION)
    blocks = find_blocks(frame, TEMPLATES)

    if not blocks:
        print("Блоки не найдены.")
        continue

    moves = check_possible_moves(blocks)
    if moves:
        # Берем первый доступный ход
        (i1, j1), (i2, j2) = moves[0]
        start_x = GAME_REGION[0] + i1 * BLOCK_SIZE + BLOCK_SIZE // 2
        start_y = GAME_REGION[1] + j1 * BLOCK_SIZE + BLOCK_SIZE // 2
        end_x = GAME_REGION[0] + i2 * BLOCK_SIZE + BLOCK_SIZE // 2
        end_y = GAME_REGION[1] + j2 * BLOCK_SIZE + BLOCK_SIZE // 2

        # Выполняем перемещение, если нужно
        move_and_drag(start_x, start_y, end_x - start_x, end_y - start_y)
    else:
        print("Ходы не найдены.")

print("Скрипт завершен.")
