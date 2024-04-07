#Создай собственный Шутер!
from random import randint
from pygame import *
from time import time as timer
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    elif hasattr(sys, "_METPASS2"):
        return os.path.join(sys._MEIPASS2, relative_path)
    else:
        return os.path.join(os.path.abspath("."), relative_path)

image_folder = resource_path(".")

WIDTH = 700
HEIGHT = 500
FPS = 60
LOST = 0
SCORE = 0 
GOAL =20
MAX_LOST = 15
LIFE =3

WHITE = (255, 255, 255)
RED = (150,0,0)
GREEN =(254,234,213)
#cprate
snd_fire = os.path.join(image_folder,"fire.ogg")
img_hero=os.path.join(image_folder,"rocket.png")
img_ufo=os.path.join(image_folder,"ufo.png")
img_back=os.path.join(image_folder,"galaxy.jpg")
snd_back=os.path.join(image_folder,"space.ogg")
img_bullet=os.path.join(image_folder,"bullet.png")
img_asteroid=os.path.join(image_folder,"asteroid.png")

mixer.init()
font.init()

font_text = font.Font(None, 80)
font_reload = font.Font(None, 36)

win_text = font_text.render("YOU WIN!", True, GREEN)
lose_text = font_text.render("YOU LOSE!", True, RED)


mixer.music.load(snd_back)
mixer.music.play()
mixer.music.set_volume(0.1)

fire = mixer.Sound(snd_fire)
fire.set_volume(1.0)

window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Шутер")
background = transform.scale(image.load(img_back), (WIDTH, HEIGHT ))
clock  = time.Clock()

class GameSprite(sprite.Sprite):
    def __init__(self, p_image: str, x: int, y: int, w:int, h: int, speed: int):
        super().__init__()
        self.image = transform.scale(image.load(p_image), (w,h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, p_image: str, x: int, y: int, w:int, h: int, speed: int,max_bullets:int):
        super().__init__(p_image, x, y, w, h, speed)
        self.max_bullets = max_bullets
        self.current_bullets = max_bullets

    def update(self):
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x> 5:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < WIDTH - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)
        self.current_bullets -=1

    def reload(self):
        self.current_bullets = self.max_bullets
        

class Enemy(GameSprite):
    def update(self):
        global LOST
        self.rect.y+=self.speed
        if self.rect.y>=HEIGHT:
            self.rect.x= randint(80, WIDTH - 80)
            self.rect.y=0
            LOST+=1
        
        
   


class Bullet(GameSprite):
    def update(self):
        self.rect.y+=self.speed
        if self.rect.y < 0:
            self.kill()
            
class AmmoIndicator(sprite.Sprite):
    def __init__(self, p_image: str, x: int, y: int, w:int, h: int, speed: int,max_bullets:int):
        super().__init__()
        self.image = transform.scale(image.load(p_image), (w,h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.max_bullets = max_bullets

    def update(self, current_bullets):
        self.rect.x = WIDTH - self.rect.width - 10
        self.rect.y = HEIGHT - self.rect.height - 10
        for i in range(self.max_bullets):
            if i < current_bullets:
                window.blit(self.image, (self.rect.x - i * (self.rect.width +5), self.rect.y))


player = Player(img_hero, 5, HEIGHT - 100,80,100,6,10)

bullets = sprite.Group()

ammo_indicator = AmmoIndicator(img_bullet, WIDTH - 10, HEIGHT - 10, 15, 20, 5,10)

monsters = sprite.Group()
for i in range(6):
    monster=Enemy(img_ufo,randint(80, WIDTH - 80), - 40,80,50,randint(1,3 ))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(3):
    asteroid=Enemy(img_asteroid,randint(80, WIDTH - 80), - 40,80,50,randint(1,5 ))
    asteroids.add(asteroid)


run = True
finish = False
rel_time = False

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                if player.current_bullets != 0 and not rel_time:
                    player.fire()
                    fire.play()
                else:
                    last_time = timer()
                    rel_time = True
                       
    if not finish:
        window.blit(background, (0, 0))
        player.reset()
        player.update()

        asteroids.update()
        asteroids.draw(window)

        monsters.update()
        monsters.draw(window)

        bullets.update()
        bullets.draw(window)

        ammo_indicator.update(player.current_bullets)

        if rel_time:
            now_time = timer()
            if now_time - last_time <1:
                reload_text = font_reload.render("ПЕРЕЗАРЯДКА...", True, RED)
                window.blit(reload_text, (260,460))
            else:
                player.reload()
                rel_time = False


        collides = sprite.groupcollide(monsters, bullets, True, True)
        for collide in collides:
            SCORE += 1
            monster=Enemy(img_ufo,randint(80, WIDTH - 80), - 40,80,50,randint(1,3))
            monsters.add(monster)

        if sprite.spritecollide(player, monsters, False) or sprite.spritecollide(player, asteroids, False):
            sprite.spritecollide(player, monsters, True)
            sprite.spritecollide(player, asteroids, True)
            LIFE -= 1

        sprite.groupcollide(asteroids, bullets, False, True)

        if SCORE >= GOAL:
            finish = True
            window.blit(win_text, (200,200))
            mixer.music.stop()

        if LIFE == 0 or LOST >= MAX_LOST:
            finish = True
            window.blit(lose_text, (200,200))
            mixer.music.stop()


        text_score = font_reload.render("Счет:" + str(SCORE), True, WHITE)
        window.blit(text_score, (10,20))

        text_lost =  font_reload.render("Пропущуноо:" + str(LOST), True, WHITE)
        window.blit(text_lost, (10,50))

        if LIFE >= 3:
            life_color = (0,150,0)
        if LIFE ==2:
            life_color = (150,150,0)
        if LIFE ==1:
            life_color = (150,0,0)

        text_life = font_reload.render("Жизни:" + str(LIFE), True, WHITE)
        window.blit(text_life, (10,80))

    else:
        SCORE = 0
        LOST = 0
        LIFE = 3
        finish = False
        player.reload()


        for m in monsters:
            m.kill()

        for a in asteroids:
            a.kill()

        for b in bullets:
            b.kill()

        time.delay(3000)

        for i in range(6):
            monster=Enemy(img_ufo,randint(80, WIDTH - 80), - 40,80,50,randint(1,3 ))
            monsters.add(monster)
        
    
    display.update()
    clock.tick(FPS)