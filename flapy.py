from pygame import *
from random import randint


font.init()


WIDTH = 460
HEIGHT = 500
BOTTOM = 420
TOP = 80
FPS = 60

WHITE = (255, 255, 255)

ground_scroll = 0
scroll_speed = 2

flying = False
finish = False
score = 0

pipe_gap = 100
pipe_frequency = 1500
last_pipe = time.get_ticks() - pipe_frequency
pas_pipe = False


window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Flappy Bird")
clock = time.Clock()
text_font = font.Font(None, 50)

background = transform.scale(image.load("bg.png"), (WIDTH, HEIGHT))
ground_img = transform.scale(image.load("ground.png"), (480, 80))
restart_img = image.load("restart.png")

def draw(text:str,  text_col: tuple, x: int, y: int) -> None:
    img = text_font.render(text,True, text_col)
    window.blit(img, (x,y))

def reset_game() -> int:
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = HEIGHT // 2
    score = 0
    return score


class Bird(sprite.Sprite):
    def __init__(self, x: int, y:int,w:int,h:int):
        super().__init__()
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1,4):                                
            img = transform.scale(image.load(f"bird{num}.png"), (w,h))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            self.vel += 0.2
            if self.vel > 30:
                self.vel = 0
            if self.rect.bottom < BOTTOM:
                self.rect.y += int(self.vel)
        if not finish:
            if mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -5
            if mouse.get_pressed()[0] == 0:
                self.clicked = False

            self.counter += 1
            flap_cooldown = 5
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                
            self.image = self.images[self.index]
            self.image = transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = transform.rotate(self.images[self.index], -90)


class Pipe(sprite.Sprite):
    def __init__(self, x: int, y: int, w: int, h: int, position: int):
        super().__init__()
        self.image = transform.scale(image.load("pipe.png"), (w,h))
        self.rect = self.image.get_rect()

        if position == 1:
            self.image = transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap // 2]
        elif position == -1:
            self.rect.topleft = [x, y + pipe_gap // 2]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x: int, y: int, image: str):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = mouse.get_pos()
        if self.rect.collidepoint(pos):
            if mouse.get_pressed()[0] == 1:
                action = True

        window.blit(self.image, (self.rect.x, self.rect.y))

        return action


bird_group = sprite.Group()
flappy = Bird(100, WIDTH // 2, 35, 25)
bird_group.add(flappy)

pipe_group = sprite.Group()

btn_restart = Button(WIDTH //2 - 50, HEIGHT // 2 - 50,restart_img )



run = True

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == MOUSEBUTTONDOWN and not flying and not finish:
            flying = True
    
    window.blit(background, (0,0))
    window.blit(ground_img,(ground_scroll, BOTTOM))

    
    pipe_group.draw(window)
    pipe_group.update()

    bird_group.draw(window)
    bird_group.update()

    ground_scroll -= scroll_speed + 0.3
    if abs(ground_scroll) > 20:
        ground_scroll = 0

   

    if sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        finish = True

    if flappy.rect.bottom >= BOTTOM:
        finish = True
        flying = False


    if not finish and flying:
        time_now = time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = randint(-50,50)
            btm_pipe = Pipe(WIDTH, HEIGHT // 2 + pipe_height, 35,250, -1)
            top_pipe = Pipe(WIDTH, HEIGHT // 2 + pipe_height, 35,250, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

    if finish:
        if btn_restart.draw():
            finish = False
            score = reset_game()

    display.update()
    clock.tick(FPS)