import tkinter as tk,sys,json,random
from random import Random
import cv2
import customtkinter as Ctk
from tkinter import *
from customtkinter import *
import pygame,sys
from pygame.locals import *
from PIL import *
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
cols = 5
rows = 6
clock = pygame.time.Clock()
fps = data['speed']
live_ball = False
game_over = 0

# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# brick wall class
class Wall():
    def __init__(self):
        self.width = scrw // cols
        self.height = 50

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
                    block_col = bg
                    block_outline = block_gold_outline
                elif block[1] == 2:
                    block_col = bg
                    block_outline = block_magenta_outline
                elif block[1] == 3:
                    block_col = bg
                    block_outline = block_teal_outline

                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, block_outline, block[0], 2)

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
        self.width = int(200)
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
        collision_thresh = 5
        # no wall in beginning
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
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                    # Power-up: 5 Ball
                    if random.random() < 0.05:  # 5% chance of power-up
                        spawn_5_balls()

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

        # check for collision with walls
        if self.rect.left < 0 or self.rect.right > scrw:
            self.speed_x *= -1
        # check for collision with top and bottom of the screen
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > scrh:
            self.game_over = -1
            self.live_ball = False
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
        self.speed_max = 5
        self.game_over = 0
        self.live_ball = True
def spawn_5_balls():
    for _ in range(5):
        x = random.randint(50, scrw - 50)
        y = random.randint(50, scrh - 50)
        new_ball = GameBall(x, y)
        balls.append(new_ball)

# create a wall
wall = Wall()
wall.create_wall()

# create paddle
player_paddle = Paddle()

# create initial ball
balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
live_ball = False
run = True
while run:
    clock.tick(fps)
    screen.fill((0, 0, 0))
    # draw all objects
    wall.draw_wall()
    player_paddle.draw()

    for ball in balls:
        ball.draw()

        if ball.live_ball:
            # draw paddle
            player_paddle.move()
            # draw ball
            game_over = ball.move()
            if game_over != 0:
                ball.live_ball = False

    # Check if all balls are not live
    if not any(ball.live_ball for ball in balls):
        live_ball = False

    # print player instructions
    if not live_ball:
        if game_over == 0:
            draw_text('space to play', font, text_col, scrw / 2 - 170, scrh // 2 + 100)
        elif game_over == 1:
            draw_text('Congrashulashins!', font, text_col, scrw / 2 - 110, scrh / 2 + 100)
            draw_text('Play again', font, text_col, scrw / 2 - 130, scrh / 2 + 100)
            draw_text('Press esc to exit', font, text_col, scrw / 2 - 130, scrh / 2 + 300)
        elif game_over == -1:
            draw_text('SKILL ISSUE', font, text_col, scrw / 2 - 130, scrh / 2 + 100)
            draw_text('Press esc to give up', font, text_col, scrw / 2 - 190, scrh / 2 + 300)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and live_ball == False:
            live_ball = True
            balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
            player_paddle.reset()
            wall.create_wall()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                with open('settings.txt', 'w') as setfile:
                    json.dump(data, setfile)
                pygame.quit()
                sys.exit(0)  # add pause later
            else:
                with open('settings.txt', 'w') as setfile:
                    json.dump(data, setfile)
        if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
            live_ball = True
            balls = [GameBall(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)]
            player_paddle.reset()
            wall.create_wall()
        if event.type == pygame.QUIT:
            with open('settings.txt', 'w') as setfile:
                json.dump(data, setfile)
            pygame.quit()
            sys.exit()

    pygame.display.update()

pygame.display.quit()
pygame.quit()