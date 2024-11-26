import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Define colors
WHITE = (255, 255, 255)
BLUE = (50, 153, 213)
GREEN = (0, 255, 0)
RED = (213, 50, 80)  # Color for the food
YELLOW = (255, 255, 0)  # Color for the "Game Over" message

# Snake block dimensions
block_size = 10

# Clock for speed control
clock = pygame.time.Clock()
speed = 15

# Font for score and messages
font = pygame.font.SysFont("bahnschrift", 25)
game_over_font = pygame.font.SysFont("bahnschrift", 50)

# Function to display the score
def show_score(score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, [10, 10])

# Function to display the "Game Over" message
def game_over_screen():
    screen.fill(BLUE)
    game_over_message = game_over_font.render("GAME OVER", True, YELLOW)
    restart_message = font.render("Press R to Restart or Q to Quit", True, WHITE)

    screen.blit(game_over_message, [WIDTH // 4, HEIGHT // 3])
    screen.blit(restart_message, [WIDTH // 4, HEIGHT // 2])
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    waiting = False
                    return True  # Return True to restart
                elif event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    quit()
    return False  # Shouldn't happen but added for safety

# Function to show the start screen
def start_screen():
    screen.fill(BLUE)
    message = font.render("Press S to start", True, WHITE)
    screen.blit(message, [WIDTH // 3, HEIGHT // 3])
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    waiting = False

# Main game loop
def main():
    # Snake properties
    x = WIDTH // 2
    y = HEIGHT // 2
    x_change = 0
    y_change = 0
    snake_body = []
    snake_length = 1

    # Food position
    food_x = random.randint(0, (WIDTH // block_size) - 1) * block_size
    food_y = random.randint(0, (HEIGHT // block_size) - 1) * block_size

    # Score
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = block_size
                    x_change = 0

        # Update the block position
        x += x_change
        y += y_change

        # Check if the snake hits the wall
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            if game_over_screen():
                return  # Restart the game
            else:
                running = False  # Quit the game

        # Clear the screen
        screen.fill(BLUE)

        # Draw the food
        pygame.draw.rect(screen, RED, [food_x, food_y, block_size, block_size])

        # Add the new position to the snake's body
        snake_body.append([x, y])
        if len(snake_body) > snake_length:
            del snake_body[0]  # Remove the oldest segment to maintain the length

        # Draw the snake
        for segment in snake_body:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], block_size, block_size])

        # Check if the snake eats the food
        if x == food_x and y == food_y:
            # Increase the length of the snake
            snake_length += 1
            # Increase the score
            score += 1
            # Generate new food position
            food_x = random.randint(0, (WIDTH // block_size) - 1) * block_size
            food_y = random.randint(0, (HEIGHT // block_size) - 1) * block_size

        # Check if the snake collides with itself
        for segment in snake_body[:-1]:
            if segment == [x, y]:
                if game_over_screen():
                    return  # Restart the game
                else:
                    running = False  # Quit the game

        # Show the score
        show_score(score)

        # Update the display
        pygame.display.update()

        # Control the speed
        clock.tick(speed)

    pygame.quit()

# Run the game
start_screen()
while True:
    main()
