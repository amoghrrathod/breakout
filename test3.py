import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_RADIUS = 15
BRICK_WIDTH, BRICK_HEIGHT = 80, 30
PADDLE_SPEED = 10
BALL_SPEED_X, BALL_SPEED_Y = 5, 5
BRICK_ROWS, BRICK_COLS = 5, 10

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Power-up colors
POWERUP_COLORS = [YELLOW, GREEN]

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Game")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Define the paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 30)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PADDLE_SPEED

# Define the ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y

    def update(self):
        # Move the ball
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Bounce off walls
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top < 0:
            self.speed_y = -self.speed_y

        # Check collision with paddle
        if pygame.sprite.collide_rect(self, paddle):
            self.speed_y = -self.speed_y

        # Check collision with bricks
        brick_collision = pygame.sprite.spritecollide(self, bricks, True)
        if brick_collision:
            self.speed_y = -self.speed_y
            # Spawn a power-up
            if random.random() < 0.1:  # 10% chance to spawn a power-up
                spawn_powerup()

# Define the brick class
class Brick(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface((BRICK_WIDTH, BRICK_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Define the power-up class
class Powerup(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_y = 3

    def update(self):
        # Move the power-up
        self.rect.y += self.speed_y

# Create sprite groups
all_sprites = pygame.sprite.Group()
bricks = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Create the paddle, ball, and bricks
paddle = Paddle()
ball = Ball()
all_sprites.add(paddle, ball)

for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        color = random.choice([WHITE, YELLOW, GREEN])
        brick = Brick(color, col * BRICK_WIDTH, row * BRICK_HEIGHT)
        bricks.add(brick)
        all_sprites.add(brick)

def spawn_powerup():
    powerup_color = random.choice(POWERUP_COLORS)
    powerup = Powerup(powerup_color, ball.rect.x, ball.rect.y)
    powerups.add(powerup)
    all_sprites.add(powerup)

# Game loop
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Update sprites
    all_sprites.update()

    # Check if all bricks are destroyed
    if len(bricks) == 0:
        print("You won!")
        run = False

    # Check collision with power-ups
    powerup_collision = pygame.sprite.spritecollide(paddle, powerups, True)
    for powerup in powerup_collision:
        # Apply power-up effects (for now, only multi-ball)
        if powerup.rect.y > HEIGHT / 2:  # Avoid applying power-ups from the bottom
            spawn_powerup()

    # Draw everything
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Refresh the screen
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
