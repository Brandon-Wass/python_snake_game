#!/usr/bin/env python3

import pygame
import random
import sys
import json
import os

os.environ["SDL_AUDIODRIVER"] = "dummy"

pygame.init()

info = pygame.display.Info()

SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
CELL_SIZE = 20

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

MENU = 0
LOADING = 1
PLAYING = 2
GAME_OVER = 3
PAUSE = 4
LEVEL_SELECTION = 5

EASY_LEVEL = 6
MEDIUM_LEVEL = 7
HARD_LEVEL = 8
EXPERT_LEVEL = 9

FONT = pygame.font.Font(None, 36)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.body = []
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.grow = False
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        for i in range(5):
            self.body.append((start_x - i * CELL_SIZE, start_y))

    def move(self):
        head = self.body[0]
        x, y = self.direction
        new_head = (head[0] + x * CELL_SIZE, head[1] + y * CELL_SIZE)
        if new_head in self.body[1:] or new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT:
            return False
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        return True

    def grow_snake(self):
        self.grow = True

    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))

    def get_direction_as_string(self):
        direction_map = {UP: "Up", DOWN: "Down", LEFT: "Left", RIGHT: "Right"}
        return direction_map.get(self.direction, "Unknown")

def generate_obstacles():
    obstacles = []

    for _ in range(2):
        obstacle_length = random.randint(4, 10) * CELL_SIZE
        obstacle_x = random.randint(0, (SCREEN_WIDTH - obstacle_length) // CELL_SIZE) * CELL_SIZE
        obstacle_y = random.randint(0, (SCREEN_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacles.append((obstacle_x, obstacle_y, obstacle_length, CELL_SIZE))

    for _ in range(2):
        obstacle_length = random.randint(4, 10) * CELL_SIZE
        obstacle_x = random.randint(0, (SCREEN_WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacle_y = random.randint(0, (SCREEN_HEIGHT - obstacle_length) // CELL_SIZE) * CELL_SIZE
        obstacles.append((obstacle_x, obstacle_y, CELL_SIZE, obstacle_length))

    for _ in range(2):
        obstacle_x = random.randint(0, (SCREEN_WIDTH - 4 * CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacle_y = random.randint(0, (SCREEN_HEIGHT - 3 * CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacles.append((obstacle_x, obstacle_y, 3 * CELL_SIZE, CELL_SIZE))
        obstacles.append((obstacle_x, obstacle_y + CELL_SIZE * 2, CELL_SIZE, 2 * CELL_SIZE))

    for _ in range(2):
        obstacle_x = random.randint(0, (SCREEN_WIDTH - 3 * CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacle_y = random.randint(0, (SCREEN_HEIGHT - 4 * CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacles.append((obstacle_x, obstacle_y, 3 * CELL_SIZE, CELL_SIZE))
        obstacles.append((obstacle_x + CELL_SIZE, obstacle_y + CELL_SIZE, CELL_SIZE, 3 * CELL_SIZE))

    for _ in range(2):
        obstacle_x = random.randint(0, (SCREEN_WIDTH - 3 * CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacle_y = random.randint(0, (SCREEN_HEIGHT - 3 * CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        obstacles.append((obstacle_x, obstacle_y, 3 * CELL_SIZE, CELL_SIZE))
        obstacles.append((obstacle_x, obstacle_y + CELL_SIZE, CELL_SIZE, CELL_SIZE))
        obstacles.append((obstacle_x + CELL_SIZE, obstacle_y + CELL_SIZE, 2 * CELL_SIZE, CELL_SIZE))
        obstacles.append((obstacle_x + 2 * CELL_SIZE, obstacle_y + 2 * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    return obstacles

def draw_obstacles(obstacles):
    for obstacle in obstacles:
        pygame.draw.rect(screen, BLUE, obstacle)

class Food:
    def __init__(self, obstacles):
        self.obstacles = obstacles
        self.food_list = [self.new_position() for _ in range(10)]
        self.food_eaten = 0

    def new_position(self):
        while True:
            position = (random.randint(0, (SCREEN_WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE,
                        random.randint(0, (SCREEN_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE)
            if not any(self.position_in_obstacle(position, obstacle) for obstacle in self.obstacles):
                return position

    @staticmethod
    def position_in_obstacle(position, obstacle):
        obstacle_rect = pygame.Rect(obstacle)
        return obstacle_rect.collidepoint(position)

    def draw(self):
        for food_position in self.food_list:
            pygame.draw.rect(screen, RED, (food_position[0], food_position[1], CELL_SIZE, CELL_SIZE))

    def food_eaten_update(self):
        self.food_eaten += 1
        if self.food_eaten % 5 == 0:
            return True
        return False

home_dir = os.path.expanduser("~")

def move_random_obstacles(obstacles, snake_body, food_positions):
    moved_obstacles = random.sample(obstacles, min(2, len(obstacles)))
    for obstacle in moved_obstacles:
        obstacles.remove(obstacle)
        def is_valid_position(new_obstacle):
            if new_obstacle[0] < 0 or new_obstacle[0] + new_obstacle[2] > SCREEN_WIDTH or new_obstacle[1] < 0 or new_obstacle[1] + new_obstacle[3] > SCREEN_HEIGHT:
                return False
            if any(snake_segment in [(x, y) for x in range(new_obstacle[0], new_obstacle[0] + new_obstacle[2], CELL_SIZE) for y in range(new_obstacle[1], new_obstacle[1] + new_obstacle[3], CELL_SIZE)] for snake_segment in snake_body):
                return False
            for other_obstacle in obstacles:
                if pygame.Rect(new_obstacle).colliderect(pygame.Rect(other_obstacle)):
                    return False
            for food_position in food_positions:
                if pygame.Rect(new_obstacle).collidepoint(food_position):
                    return False
            return True
        while True:
            new_x = random.randint(0, (SCREEN_WIDTH - obstacle[2]) // CELL_SIZE) * CELL_SIZE
            new_y = random.randint(0, (SCREEN_HEIGHT - obstacle[3]) // CELL_SIZE) * CELL_SIZE
            new_obstacle = (new_x, new_y, obstacle[2], obstacle[3])
            if is_valid_position(new_obstacle):
                obstacles.append(new_obstacle)
                break
            else:
                obstacles.append(obstacle)
                break

def load_high_scores():
    try:
        with open(f"{home_dir}/high_scores.json", "r") as file:
            high_scores = json.load(file)
    except FileNotFoundError:
        high_scores = {"easy": [], "medium": [], "hard": [], "expert": []}
    return high_scores

def save_high_scores(high_scores):
    with open(f"{home_dir}/high_scores.json", "w") as file:
        json.dump(high_scores, file)

def update_high_scores(high_scores, score, level):
    level_key = {EASY_LEVEL: "easy", MEDIUM_LEVEL: "medium", HARD_LEVEL: "hard", EXPERT_LEVEL: "expert"}[level]
    if score not in high_scores[level_key]:
        high_scores[level_key].append(score)
        high_scores[level_key].sort(reverse=True)
        high_scores[level_key] = high_scores[level_key][:5]
    return high_scores

def display_high_scores(high_scores, level):
    level_key = {EASY_LEVEL: "easy", MEDIUM_LEVEL: "medium", HARD_LEVEL: "hard", EXPERT_LEVEL: "expert"}[level]
    scores = high_scores[level_key]
    if scores:
        show_text(f"{level_key.capitalize()} Level High Scores:", WHITE, 50)
        for i, score in enumerate(scores):
            show_text(f"{i + 1} ----> {score}", WHITE, (100 + (i * 50)))
    else:
        show_text("No High Scores Yet", WHITE)

def show_text(text, color, y_offset=0):
    text_surface = FONT.render(text, True, color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)

def draw_pause_overlay():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    show_text("Game Paused", WHITE, -50)
    show_text("Press ENTER to resume", WHITE, 0)
    show_text("Press ESC to forfeit", WHITE, 50)
    pygame.display.flip()

def main():
    high_scores = load_high_scores()
    snake = Snake()
    obstacles = generate_obstacles()
    food = Food(obstacles)
    score = 0
    state = MENU
    speed = 10
    CURSOR_HIDE_TIME = 1000
    last_mouse_movement = pygame.time.get_ticks()
    cursor_hidden = False

    while True:
        if pygame.time.get_ticks() - last_mouse_movement > CURSOR_HIDE_TIME and not cursor_hidden:
            pygame.mouse.set_visible(False)
            cursor_hidden = True
        elif pygame.mouse.get_rel() != (0, 0):
            pygame.mouse.set_visible(True)
            last_mouse_movement = pygame.time.get_ticks()
            cursor_hidden = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if state == MENU:
                    if event.key == pygame.K_RETURN:
                        state = LEVEL_SELECTION
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif state == LEVEL_SELECTION:
                    if event.key == pygame.K_1:
                        snake = Snake()
                        obstacles = []
                        food = Food(obstacles)
                        score = 0
                        speed = 10
                        level = EASY_LEVEL
                        state = LOADING
                    if event.key == pygame.K_2:
                        snake = Snake()
                        obstacles = generate_obstacles()
                        food = Food(obstacles)
                        score = 0
                        speed = 15
                        level = MEDIUM_LEVEL
                        state = LOADING
                    if event.key == pygame.K_3:
                        snake = Snake()
                        obstacles = generate_obstacles()
                        food = Food(obstacles)
                        score = 0
                        speed = 20
                        level = HARD_LEVEL
                        state = LOADING
                    if event.key == pygame.K_4:
                        snake = Snake()
                        obstacles = generate_obstacles()
                        food = Food(obstacles)
                        score = 0
                        speed = 25
                        level = EXPERT_LEVEL
                        state = LOADING
                elif state == PLAYING and level in [EASY_LEVEL, MEDIUM_LEVEL, HARD_LEVEL, EXPERT_LEVEL]:
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
                elif state == GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        snake = Snake()
                        obstacles = generate_obstacles()
                        food = Food(obstacles)
                        score = 0
                        speed = 10
                        state = MENU
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if state == PLAYING and event.key == pygame.K_ESCAPE:
                    state = PAUSE
                elif state == PAUSE:
                    if event.key == pygame.K_RETURN:
                        state = PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        state = GAME_OVER
        if state == MENU:
            screen.fill(BLACK)
            show_text("Snake Game", WHITE, -250)
            show_text("Press ENTER to choose level", WHITE, -150)
            show_text("Press ESC to quit", WHITE, -100)
            show_text("In-Game Controls:", WHITE, 0)
            show_text("Move Up    -->    Up Arrow", WHITE, 50)
            show_text("Move Left  -->  Left Arrow", WHITE, 100)
            show_text("Move Down  -->  Down Arrow", WHITE, 150)
            show_text("Move Right --> Right Arrow", WHITE, 200)
            show_text("Pause Game -->      Escape     ", WHITE, 250)
            pygame.display.flip()
        if state == LEVEL_SELECTION:
            screen.fill(BLACK)
            show_text("Press 1 for EASY difficulty", WHITE, -250)
            show_text("Speed = 10, NO speed increase, NO obstacles", WHITE, -200)
            show_text("Press 2 for MEDIUM difficulty", WHITE, -100)
            show_text("Speed = 15, NO speed increase, YES obstacles", WHITE, -50)
            show_text("Press 3 for HARD difficulty", WHITE, 50)
            show_text("Speed = 20, YES speed increase +0.25 per food, YES obstacles", WHITE, 100)
            show_text("Press 4 for EXPERT difficulty", WHITE, 200)
            show_text("Speed = 25, YES speed increase +1.0 per food, YES obstacles randomly move per 5 food", WHITE, 250)
            pygame.display.flip()
        if state == LOADING:
            countdown_time = 5
            start_ticks = pygame.time.get_ticks()
            while countdown_time > 0:
                screen.fill(BLACK)
                seconds = (pygame.time.get_ticks() - start_ticks) / 1000
                if seconds > 1:
                    countdown_time -= 1
                    start_ticks = pygame.time.get_ticks()
                countdown_message = f"Starting new match in {countdown_time}"
                show_text(countdown_message, WHITE)
                pygame.display.flip()
            state = PLAYING
        if state == PLAYING and level in [EASY_LEVEL, MEDIUM_LEVEL, HARD_LEVEL, EXPERT_LEVEL]:
            screen.fill(BLACK)
            if level == EXPERT_LEVEL:
                if not snake.move():
                    state = GAME_OVER
                for food_position in food.food_list:
                    if snake.body[0] == food_position:
                        snake.grow_snake()
                        food.food_list.remove(food_position)
                        food.food_list.append(food.new_position())
                        score += 1
                        if food.food_eaten_update():
                            move_random_obstacles(obstacles, snake.body, [food_position for food_position in food.food_list])
                        if score % 1 == 0:
                            speed += 1
                for obstacle in obstacles:
                    if snake.body[0] in [(x, y) for x in range(obstacle[0], obstacle[0] + obstacle[2], CELL_SIZE) for y in range(obstacle[1], obstacle[1] + obstacle[3], CELL_SIZE)]:
                        state = GAME_OVER
                        break
                snake.draw()
                draw_obstacles(obstacles)
                food.draw()
                show_text(f"Score: {score}", WHITE, -250)
                pygame.display.flip()
            if level == HARD_LEVEL:
                if not snake.move():
                    state = GAME_OVER
                for food_position in food.food_list:
                    if snake.body[0] == food_position:
                        snake.grow_snake()
                        food.food_list.remove(food_position)
                        food.food_list.append(food.new_position())
                        score += 1
                        if score % 1 == 0:
                            speed += 0.25
                for obstacle in obstacles:
                    if snake.body[0] in [(x, y) for x in range(obstacle[0], obstacle[0] + obstacle[2], CELL_SIZE) for y in range(obstacle[1], obstacle[1] + obstacle[3], CELL_SIZE)]:
                        state = GAME_OVER
                        break
                snake.draw()
                draw_obstacles(obstacles)
                food.draw()
                show_text(f"Score: {score}", WHITE, -250)
                pygame.display.flip()
            if level == MEDIUM_LEVEL:
                if not snake.move():
                    state = GAME_OVER
                for food_position in food.food_list:
                    if snake.body[0] == food_position:
                        snake.grow_snake()
                        food.food_list.remove(food_position)
                        food.food_list.append(food.new_position())
                        score += 1
                    for obstacle in obstacles:
                        if snake.body[0] in [(x, y) for x in range(obstacle[0], obstacle[0] + obstacle[2], CELL_SIZE) for y in range(obstacle[1], obstacle[1] + obstacle[3], CELL_SIZE)]:
                            state = GAME_OVER
                            break
                    snake.draw()
                    draw_obstacles(obstacles)
                food.draw()
                show_text(f"Score: {score}", WHITE, -250)
                pygame.display.flip()
            if level == EASY_LEVEL:
                if not snake.move():
                    state = GAME_OVER
                for food_position in food.food_list:
                    if snake.body[0] == food_position:
                        snake.grow_snake()
                        food.food_list.remove(food_position)
                        food.food_list.append(food.new_position())
                        score += 1
                snake.draw()
                food.draw()
                show_text(f"Score: {score}", WHITE, -250)
                pygame.display.flip()
        if state == PAUSE:
            draw_pause_overlay()
        if state == GAME_OVER:
            screen.fill(BLACK)
            show_text("Game Over!", WHITE, -300)
            show_text(f"Score: {score}", WHITE, -200)
            show_text("Press ENTER to return to Main Menu", WHITE, -100)
            show_text("Press ESC to quit", WHITE, -50)
            high_scores = update_high_scores(high_scores, score, level)
            save_high_scores(high_scores)
            display_high_scores(high_scores, level)
            pygame.display.flip()
        pygame.display.flip()
        clock.tick(speed)

if __name__ == "__main__":
    main()