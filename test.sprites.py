import pygame
import sys
import json
import random

pygame.init()
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
# Load game settings
data = {"screen_width": 1280, "screen_height": 720, "scr": "1280x720", "speed": 90}
try:
    with open('settings.txt') as setfile:
        data = json.load(setfile)
except FileNotFoundError:
    pass

# Set up Pygame screen
scrw, scrh = 1280, 720
screen = pygame.display.set_mode((scrw, scrh))
pygame.display.set_caption('Brick-slayer')

# Colors
bg = (9, 10, 24)
block_gold_outline = (255, 215, 0)
block_magenta_outline = (255, 0, 255)
block_teal_outline = (55, 255, 255)
paddle_col = (255, 255, 255)
text_col = (255, 255, 255)

# Game variables
cols, rows = 5, 6
clock = pygame.time.Clock()
fps = data['speed']
live_ball = False
game_over = 0

# Font
font = pygame.font.SysFont('typewriter', 70)

# Sprite groups
all_sprites = pygame.sprite.Group()

# Brick wall class
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, strength):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.strength = strength

        if self.strength == 1:
            self.color = bg
            self.outline_color = block_gold_outline
        elif self.strength == 2:
            self.color = bg
            self.outline_color = block_magenta_outline
        elif self.strength == 3:
            self.color = bg
            self.outline_color = block_teal_outline

        pygame.draw.rect(self.image, self.color, (0, 0, width, height), 1, 1)
        pygame.draw.rect(self.image, self.outline_color, (0, 0, width, height), 2)
        pygame.draw.rect(self.image, bg, (0, 0, width, height), 1, 1)

# Paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.image.load('assets/paddle_purple.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.reset()

    def move(self):
        self.direction = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if keys[pygame.K_RIGHT] and self.rect.right < scrw:
            self.rect.x += self.speed
            self.direction = 1

    def reset(self):
        self.height = 25
        self.width = int(200)
        self.x = int((scrw / 2) - (self.width / 2))
        self.y = scrh - (self.height * 2)
        self.speed = 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/ball.png').convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.reset(x, y)

    def move(self):
        # Collision threshold
        collision_thresh = 5
        wall_destroyed = 1
        row_count = 0

        for row in wall.blocks:
            item_count = 0
            for item in row:
                # Check collision
                if self.rect.colliderect(item[0]):
                    # Check if collision was from above
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                    # Check if collision was from below
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1
                    # Check if collision was from left
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1 / 2
                    # Check if collision was from right
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1 / 2

                    # Reduce the block's strength by doing damage to the block
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                # Check if block still exists, in which case the wall is not destroyed
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0

                # Increase item counter
                item_count += 1

            # Increase row counter
            row_count += 1

        # After iterating through all the blocks, check if the wall is destroyed
        if wall_destroyed == 1:
            self.game_over = 1

        # Check for collision with walls
        if self.rect.left < 0 or self.rect.right > scrw:
            self.speed_x *= -1

        # Check for collision with top and bottom of the screen
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > scrh:
            self.game_over = -1

        # Look for collision with paddle
        if self.rect.colliderect(player_paddle):
            # Check if colliding from the top
            if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += player_paddle.direction
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
            else:
                self.speed_x *= -1

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def reset(self, x, y):
        self.ball_rad = 11
        self.x = x - self.ball_rad
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 5
        self.game_over = 0

# Create a wall
class Wall(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.create_wall()

    def create_wall(self):
        for row in range(rows):
            for col in range(cols):
                block = Block(col * (scrw // cols), row * 50, scrw // cols, 50, random.randint(1, 3))
                self.blocks.append(block)
                all_sprites.add(block)

# Create paddle
player_paddle = Paddle((scrw / 2) - 100, scrh - 50, 200, 25)
all_sprites.add(player_paddle)

# Create ball
ball = Ball(player_paddle.rect.x + (player_paddle.rect.width // 2), player_paddle.rect.y - player_paddle.rect.height)
all_sprites.add(ball)

# Create wall
wall = Wall()

# Main game loop
running = True
while running:
    clock.tick(fps)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                with open('settings.txt', 'w') as setfile:
                    json.dump(data, setfile)
                running = False

    all_sprites.update()

    if live_ball:
        player_paddle.move()
        game_over = ball.move()
        if game_over != 0:
            live_ball = False

    all_sprites.draw(screen)

    if not live_ball:
        if game_over == 0:
            draw_text('space to play', font, text_col, scrw / 2 - 170, scrh // 2 + 100)
        elif game_over == 1:
            draw_text('Congratulations!', font, text_col, scrw / 2 - 110, scrh / 2 + 100)
            draw_text('Play again', font, text_col, scrw / 2 - 130, scrh / 2 + 100)
            draw_text('Press esc to exit', font, text_col, scrw / 2 - 130, scrh / 2 + 300)
        elif game_over == -1:
            draw_text('SKILL ISSUE', font, text_col, scrw / 2 - 130, scrh / 2 + 100)
            draw_text('Press esc to give up', font, text_col, scrw / 2 - 190, scrh / 2 + 300)

    pygame.display.flip()

pygame.quit()
sys.exit()
