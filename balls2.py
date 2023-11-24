# %%
import pygame,sys,time,random,os
pygame.mixer.init()
gameover_music=''
from pygame.locals import *
pygame.init()
scr_wth = 1280
scr_hgt = 800
scr = pygame.display.set_mode((scr_wth,scr_hgt))
pygame.display.set_caption('Brick-slayer')
font = pygame.font.SysFont('typewriter', 70)
imp = pygame.image.load("/Users/amoghrathod/Brick-slayer/code/Brick/assets/wall.jpg").convert()
pygame.display.flip()
status = True
bg = (9 ,10,24)
block_gold_outline = (255,215,0)
block_magenta_outline = (255,0,255)
block_teal_outline = (55,255,255)
bar_col = (255,255,255)
bar_outline = (105,105,105)
text_col = (255,255,255)
cols = 5
rows = 6
clock = pygame.time.Clock()
fps = 165
live_ball = False
game_over=0
def d_text(text, font, text_col, x, y):
    img = font.render(text,True, text_col)
    scr.blit(img, (x, y))
class bar():
    def __init__(self):
        self.reset()

    def move(self):
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.right < (scr_wth):
            self.rect.x += self.speed
            self.direction = 1

    def draw(self):
        pygame.draw.rect(scr, bar_col , self.rect)
        pygame.draw.rect(scr, (0,0,0), self.rect,2)

    def reset(self):
        self.height = 20
        self.width = int(scr_wth / cols)
        self.x = int((scr_wth / 2) - (self.width / 2))
        self.y = scr_hgt - (self.height * 2)
        self.speed = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0
class wall():
    def __init__(self):
        self.width = scr_wth // cols
        self.height = 50

    def make_wall(self):
        self.blocks = []
        blk_each = []
        for row in range(rows):
            block_row = []
            for col in range(cols):
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                if row < 2:
                    strength = 3
                elif row < 4:
                    strength = 2
                elif row < 6:
                    strength = 1
                blk_each = [rect, strength]
                block_row.append(blk_each)
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                if block[1] == 3:
                    block_col = bg
                    block_outline = block_gold_outline
                elif block[1] == 2:
                    block_col = bg
                    block_outline = block_magenta_outline
                elif block[1] == 1:
                    block_col = bg
                    block_outline = block_teal_outline
                pygame.draw.rect(scr, block_col, block[0],6)
                pygame.draw.rect(scr, block_outline, (block[0]), 5,border_radius=10)
                pygame.draw.rect(scr, bg, (block[0]),3,border_radius=10)
class ball():
    def __init__(self, x, y):
        self.reset(x, y)
    def move(self):
        collision_thresh = 5
        wall_destroyed = 1
        row_count = 0
        for row in wall.blocks:
            item_count = 0
            for item in row:
                
                if self.rect.colliderect(item[0]):
                    
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1
                    
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1
                    
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1/2
                    
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1/2
                   
                    if wall.blocks[row_count][item_count][1] > 1:
                        wall.blocks[row_count][item_count][1] -= 1
                    else:
                        wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

                
                if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                
                item_count += 1
          
            row_count += 1
       
        if wall_destroyed == 1:
            self.game_over = 1

        
        if self.rect.left < 0 or self.rect.right > scr_wth:
            self.speed_x *= -1

        
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > scr_hgt:
            self.game_over = -1

       
        if self.rect.colliderect(usr_bar):
            
            if abs(self.rect.bottom - usr_bar.rect.top) < collision_thresh and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += usr_bar.direction
                if self.speed_x > self.maxspeed:
                    self.speed_x = self.maxspeed
                elif self.speed_x < 0 and self.speed_x < -self.maxspeed:
                    self.speed_x = -self.maxspeed
            else:
                self.speed_x *= -1

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def draw(self):
        pygame.draw.circle(scr,(255,255,255), (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad),
                           self.ball_rad)
        pygame.draw.circle(scr,bar_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad),
                           self.ball_rad,1)

    def reset(self, x, y):
        self.ball_rad = 11
        self.x = x - self.ball_rad
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.maxspeed = 5
        self.game_over = 0
class Powerup(pygame.sprite.Sprite):
    """A powerup."""
    def __init__(self, type='bigpaddle'):
        pygame.sprite.Sprite.__init__(self)

        # some variables we need
        self.type = type            # which powerup is it
        self.collected = False      # has it been collected yet?
        self.countdown = 1          # duration of the effect

        # set individual countdowns for the powerups with actual durations
        if type == 'bigpaddle':
            self.countdown = 60 * 25
        elif type == 'slowball':
            self.countdown = 60 * 10

        self.imagepaths = {
            'bigpaddle': os.path.join('assets', 'powerup_paddle.png'),
            'laser': os.path.join('assets', 'powerup_laser.png'),
            '1up': os.path.join('assets', 'powerup_lightning.png'),
            'slowball': os.path.join('assets', 'powerup_ball.png'),
        }

        # set image and rect so we can be rendered
        self.image = pygame.image.load(self.imagepaths[type])
        self.rect = self.image.get_rect()

        # set initial position somewhere near the top but below the blocks
        self.rect.center = random.randint(20, 500), 125

    def update(self):
        """Called every frame. Move the powerup down a bit so it 'falls' down
        the screen. Return false if below the screen because the player
        missed it."""
        self.rect.y += 2
        if self.rect.y > 600:
            return False
        return True
wall = wall()
wall.make_wall()
usr_bar = bar()
ball = ball(usr_bar.x + (usr_bar.width // 2), usr_bar.y - usr_bar.height)
run = True
while run:
    clock.tick(fps-20)
    scr.blit(imp, (0, 0))
    wall.draw_wall()
    usr_bar.draw()
    ball.draw()
    if live_ball:
        usr_bar.move()
        game_over = ball.move()
        if game_over != 0:
            live_ball = False
    if not live_ball:
        if game_over == 0:
            d_text('Press space to play', font, text_col, scr_wth/2 -170, scr_hgt // 2 + 100)
        elif game_over == 1:
            d_text('congrats!', font, text_col, scr_wth/2 - 110, scr_hgt /2 +100 )
            d_text('Play again', font, text_col, scr_wth/2 -130, scr_hgt /2 +100)
            d_text('Press esc to exit', font, text_col, scr_wth/2-130, scr_hgt /2 +300)
        elif game_over == -1:
            d_text('GAME OVER', font, text_col, scr_wth/2 -150, scr_hgt /2 +100)
            d_text('Press esc to return to the main menu', font, text_col, scr_wth/2 -459, scr_hgt /2 +300)
            d_text('Press space to play again', font, text_col, scr_wth/2 -269, scr_hgt /2 +200)

    for event in pygame.event.get():
        if event.type==pygame.KEYDOWN and event.key==pygame.K_f:
            pygame.display.toggle_fullscreen()
        if event.type == pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                import main
        if event.type == pygame.KEYDOWN and event.key==pygame.K_SPACE and live_ball == False:
            live_ball = True
            ball.reset(usr_bar.x + (usr_bar.width // 2), usr_bar.y - usr_bar.height)
            usr_bar.reset()
            wall.make_wall()
    pygame.display.update()
pygame.display.quit()
pygame.quit()




# %%
