import tkinter as tk,sys,json,random
from random import Random
import cv2
import customtkinter as Ctk
from tkinter import *
from customtkinter import *
import pygame,sys
from pygame.locals import *
from PIL import *
from subprocess import Popen
data = {"screen_width": 1280, "screen_height": 720, "scr": "1280x720", "speed": 90}

try:
    with open('settings.txt') as setfile:
        data = json.load(setfile)
except:
    pass

pygame.init()
scrw = 1280
scrh = 720
background = pygame.Surface((1280, 720))
screen = pygame.display.set_mode((scrw, scrh))
pygame.display.set_caption('Brick-slayer')

# define font
font = pygame.font.SysFont('typewriter', 70)

# paint screen one time
pygame.display.flip()
status = True

# colours
bg = (9, 10, 24)
# block colours
block_gold_outline = (255, 215, 0)
block_magenta_outline = (255, 0, 255)
block_teal_outline = (55, 255, 255)
# paddle colours
paddle_col = (255, 255, 255)
paddle_outline = (105, 105, 105)
# text colour
text_col = (255, 255, 255)

# define game variables
cols = 17
rows = 6
clock = pygame.time.Clock()
fps = data['speed']
live_ball = False
game_over = 0
power_ups = []
score=0
# function for outputting text onto the screen
def draw_text(text, font, text_col,y):
    img = font.render(text, True, text_col)
    text_rect = img.get_rect(center=(scrw/2,y))
    screen.blit(img, text_rect)

# brick wall class
class Wall():
    def __init__(self):
        self.width = 75
        self.height = 25
        self.blue_brick_image = pygame.image.load('assets/blue.png').convert_alpha()
        self.red_brick_image = pygame.image.load('assets/red.png').convert_alpha()
        self.gold_brick_image = pygame.image.load('assets/gold.png').convert_alpha()


    def create_wall(self):
        self.blocks = []
        # define an empty list for an individual block
        block_individual = []
        for row in range(rows):
            # reset the block row list
            block_row = []
            # iterate through each column in that row
            for col in range(cols):
                # generate x and y positions for each block and create a rectangle from that
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                # give strength randomly to the blocks
                strength = random.randint(1, 3)
                # create a list at this point to store the rect and colour data
                block_individual = [rect, strength]
                # append that individual block to the block row
                block_row.append(block_individual)
            # append the row to the full list of blocks
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                # assign a colour based on block strength
                if block[1] == 1:
                    brick_image = self.gold_brick_image
                elif block[1] == 2:
                    brick_image = self.red_brick_image
                elif block[1] == 3:
                    brick_image = self.blue_brick_image
                # Convert the position and size to a pygame.Rect
                block_rect = pygame.Rect(block[0])

                # Get the center of the block rectangle
                center_x, center_y = block_rect.center

                # Calculate the position to blit the image
                img_rect = brick_image.get_rect(center=(center_x, center_y))

                # Draw the brick image
                screen.blit(brick_image, img_rect)
                
# paddle class
class Paddle():
    def __init__(self):
        self.reset()
        self.image=pygame.image.load('assets/paddle_purple.png').convert_alpha()

    def move(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.x = mouse_x - self.width // 2
        self.y = scrh - self.height
        self.rect = Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def reset(self):
        # define paddle variables
        self.height = 25
        self.width = 200
        self.x = int((scrw / 2) - (self.width / 2))
        self.y = scrh - (self.height * 2)
        self.speed = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

# ball class
class GameBall():
    def __init__(self, x, y):
        self.reset(x, y)
        self.image = pygame.image.load('assets/ball.png').convert_alpha()

    def move(self):
        # collision threshold
        collision_thresh = 6
        wall_destroyed = 1
        row_count = 0

        for row in wall.blocks:
            item_count = 0
            for item in row:
                # check collision
                if self.rect.colliderect(item[0]):
                    # check if collision was from above
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                    # check if collision was from below
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1
                    # check if collision was from left
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1 / 2
                    # check if collision was from right
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1 / 2

                    # reduce the block's strength by doing damage to block
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                        global score
                        score += 10
                        
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                    # Power-up: 5 Ball
                    if random.random() < 0.1:  # 5% chance of power-up
                        powerup.spawn_power_ups()


                # check if block still exists, in which case the wall is not destroyed
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0

                # increase item counter
                item_count += 1

            # increase row counter
            row_count += 1

        # after iterating through all the blocks, check if the wall is destroyed
        if wall_destroyed == 1:
            self.game_over = 1
        elif self.rect.bottom > scrh:
            self.game_over = -1
            self.live_ball = False    
        # check for collision with walls
        if self.rect.left < 0 or self.rect.right > scrw:
            self.speed_x *= -1
        # check for collision with top and bottom of the screen
        if self.rect.top < 0:
            self.speed_y *= -1
        
        # look for collision with paddle
        if self.rect.colliderect(player_paddle.rect):
            # check if colliding from the top
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

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def reset(self, x, y):
        self.ball_rad = 11
        self.x = x - self.ball_rad
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max = 6
        self.game_over = 0
        self.live_ball = True
    def collect_power_ups(self):
        for power_up in power_ups:
            if not power_up.is_collected() and self.rect.colliderect(
                pygame.Rect(power_up.x - power_up.radius, power_up.y - power_up.radius, 2 * power_up.radius, 2 * power_up.radius)
            ):
                power_up.collect()
    def is_off_screen(self):
        return self.rect.y > scrh
# power up class

class powerup():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = (255, 0, 0)  # Red color for the power-up
        self.collected=False
    def spawn_power_ups():
        for _ in range(5):
            x = random.randint(50, scrw - 50)
            y = random.randint(50, scrh - 50)
            new_ball = GameBall(x, y)
            balls.append(new_ball)

            # Spawn power-up at the same location as the ball
            power_up = powerup(x, y)
            power_ups.append(power_up)
    def draw_power_ups():
        for power_up in power_ups:
            if not power_up.is_collected() and not power_up.is_off_screen():
                pygame.draw.circle(screen, power_up.color, (power_up.x, power_up.y), power_up.radius)

    def is_collected(self):
        return self.collected

    def is_off_screen(self):
        return self.y > scrh

    def collect(self):
        self.collected = True

#score
def draw_score():
    score_font = pygame.font.SysFont('typewriter', 40)
    score_text = f"Score: {score}"
    draw_text(score_text, score_font, text_col, 10)
# create a wall
wall = Wall()
wall.create_wall()

# create paddle
player_paddle = Paddle()

# create initial ball
balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
live_ball = False
# before the game starts, to prevent a blank screen 
start_image = pygame.image.load('assets/Untitled.png').convert_alpha()  # Replace with the actual path to your logo image
logo_rect = start_image.get_rect()
screen.blit(start_image, (scrw / 2 - logo_rect.width / 2, scrh // 2 - logo_rect.height / 2))
pygame.display.flip()

waiting_for_input = True
while waiting_for_input:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            waiting_for_input = False
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

run = True
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
            if event.key == pygame.K_SPACE and not live_ball:
                # Start the game when space is pressed and the ball is not live
                live_ball = True
                balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
                player_paddle.reset()
                wall.create_wall()
                score = 0
            elif event.key == pygame.K_ESCAPE:
                score = 0
                with open('settings.txt', 'w') as setfile:
                    json.dump(data, setfile)
                pygame.quit()
                sys.exit(0)
            elif event.key == pygame.K_m:
                game_script_path = os.path.join(os.path.dirname(__file__), "menu.py")
                Popen(["python3", game_script_path])
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and not live_ball:
            live_ball = True
            balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
            player_paddle.reset()
            wall.create_wall()
            score = 0

    if live_ball:
        player_paddle.move()  # Move the paddle first
        for ball in balls:
            ball.collect_power_ups()
            game_over = ball.move()

            if ball.is_off_screen() or game_over != 0:
                ball.live_ball = False

        # Check if all balls are not live
        if not any(ball.live_ball for ball in balls):
            live_ball = False

        clock.tick(fps)
        screen.fill((0, 0, 0))
        # draw all objects
        wall.draw_wall()
        player_paddle.draw()
        # Draw power-ups
        powerup.draw_power_ups()

        for ball in balls:
            ball.draw()

        # print player instructions
        if not live_ball:
            if game_over == 1:
                exit_image = pygame.image.load('assets/exit.png').convert_alpha()
                exit_rect = exit_image.get_rect()
                screen.blit(exit_image, (scrw / 2 - logo_rect.width / 2, scrh // 2 - logo_rect.height / 2))
            elif game_over == -1:
                exit_image = pygame.image.load('assets/exit.png').convert_alpha()
                exit_rect = exit_image.get_rect()
                screen.blit(exit_image, (scrw / 2 - logo_rect.width / 2, scrh // 2 - logo_rect.height / 2))
        draw_score()
        pygame.display.update()

pygame.display.quit()
pygame.quit()
