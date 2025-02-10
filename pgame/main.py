import random

import pygame
import sys
import os

pygame.mixer.init()
BLACK = (0, 0, 0)
SIZE = width, height = 500, 500
FPS = 60
PLAYER_SPEED = 5  # Уменьшена скорость персонажа
WHITE = (255, 255, 255)
ground = 440  # уровень земли
JUMP_HEIGHT = 20  # сила прыжка
GRAVITY = 1  # сила гравитации
COUNT = 0
danger_list = []

count_sound = pygame.mixer.Sound('music/Звук-достижения-сохранения.ogg')
pygame.mixer.music.load('music/laxity-crosswords-by-seraphic-music.mp3')
pygame.mixer.music.play(-1)
die_sound = pygame.mixer.Sound('music/dark-souls-you-died-sound-effect_hm5sYFG.ogg')

INIT_DELAY = 2500
spawn_delay = INIT_DELAY
DECREASE_BASE = 1.01
last_spawn_time = pygame.time.get_ticks()

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Персонаж")
all_sprites = pygame.sprite.Group()  # создаем глобальную группу всех спрайтов
player_sprite = pygame.sprite.Group()
danger_sprite = pygame.sprite.Group()

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try: 
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = 250
        self.rect.y = ground
        self.speed_x = 0
        self.speed_y = 0
        self.onGround = True
        self.facing_left = False
        self.frame_rate = frame_rate
        self.frame_timer = 0
        self.is_moving = False
        self.player_out = False

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def move(self, dx):
        self.speed_x += dx
        self.rect.x += self.speed_x
        self.speed_x = 0

    def update(self):
        if self.is_moving:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_rate:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                self.frame_timer = 0
            if self.facing_left:
                self.image = pygame.transform.flip(self.frames[self.cur_frame], True, False)
        else:
            self.image = self.frames[0]
            if self.facing_left:
                self.image = pygame.transform.flip(self.frames[0], True, False)

        if not self.onGround:
            self.speed_y += GRAVITY
        if self.rect.y + self.speed_y >= ground:
            self.rect.y = ground
            self.onGround = True
            self.speed_y = 0
        else:
            self.rect.y += self.speed_y

    def jump(self):
        if self.onGround:
            self.speed_y = -JUMP_HEIGHT
            self.onGround = False


class Danger(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = height - self.rect.height
        self.frame_rate = frame_rate
        self.speed_x = 3
        self.facing_left = True
        self.player_out = True
        direction = random.randint(0, 1)
        if direction == 0:
            # Справа внизу
            self.rect.x = width - self.rect.width
            self.rect.y = height - self.rect.height
            self.speed_x = -self.speed_x  # Двигаемся влево
            self.facing_left = False
        else:
            # Слева внизу
            self.rect.x = 0
            self.rect.y = height - self.rect.height
            self.speed_x = self.speed_x  # Двигаемся вправо
            self.facing_left = True
        self.frame_timer = 0
        self.danger_life = True

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.x < -self.rect.width or self.rect.x > width:
            self.kill()
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_timer = 0

class Danger1(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = height - self.rect.height
        self.frame_rate = frame_rate
        self.speed_x = 4
        self.facing_left = True
        self.player_out = True
        direction = random.randint(0, 1)
        if direction == 0:
            # Справа внизу
            self.rect.x = width - self.rect.width
            self.rect.y = (height - self.rect.height) + 33
            self.speed_x = -self.speed_x  # Двигаемся влево
            self.facing_left = False
        else:
            # Слева внизу
            self.rect.x = 0
            self.rect.y = (height - self.rect.height) + 33
            self.speed_x = self.speed_x  # Двигаемся вправо
            self.facing_left = True
        self.frame_timer = 0
        self.danger_life = True

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.x < -self.rect.width or self.rect.x > width:
            self.kill()
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_timer = 0

class Danger2(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, scale_factor=2, frame_rate=10):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows, scale_factor)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.y = height - self.rect.height
        self.frame_rate = frame_rate
        self.speed_x = 4
        self.facing_left = True
        self.player_out = True
        direction = random.randint(0, 1)
        if direction == 0:
            # Справа внизу
            self.rect.x = width - self.rect.width
            self.rect.y = height - self.rect.height
            self.speed_x = -self.speed_x  # Двигаемся влево
            self.facing_left = False
        else:
            # Слева внизу
            self.rect.x = 0
            self.rect.y = height - self.rect.height
            self.speed_x = self.speed_x  # Двигаемся вправо
            self.facing_left = True
        self.frame_timer = 0
        self.danger_life = True

    def cut_sheet(self, sheet, columns, rows, scale_factor):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frame = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                frame = pygame.transform.scale(frame,
                                               (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
                self.frames.append(frame)
    def update(self):
        self.rect.x += self.speed_x
        if self.rect.x < -self.rect.width or self.rect.x > width:
            self.kill()
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            self.frame_timer = 0





if __name__ == '__main__':
    player_animation = Player(load_image("Owlet_Monster_Run_6.png"), 6, 1, scale_factor=1.8, frame_rate=7)
    all_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    danger_sprite = pygame.sprite.Group()

    player_sprite.add(player_animation)
    all_sprites.add(player_animation)

    clock = pygame.time.Clock()
    running = True
    last_spawn_time = pygame.time.get_ticks()
    INIT_DELAY = 2000

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.mixer.music.stop()


        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_animation.move(-PLAYER_SPEED)
            player_animation.facing_left = True
            player_animation.is_moving = True
        elif keys[pygame.K_RIGHT]:
            player_animation.move(PLAYER_SPEED)
            player_animation.facing_left = False
            player_animation.is_moving = True
        else:
            player_animation.is_moving = False

        if keys[pygame.K_UP]:
            player_animation.jump()

        now = pygame.time.get_ticks()
        if now - last_spawn_time > INIT_DELAY:
            last_spawn_time = now
            if COUNT > 0:
                third_danger = Danger2(load_image("Skeleton_01_Yellow_Walk (1).png", (255, 255, 255)), 10, 1, scale_factor=1.8, frame_rate=7)
                danger_sprite.add(third_danger)
            if COUNT > 0:
                second_danger = Danger1(load_image("NightBorne.png", (255, 255, 255)), 6, 1, scale_factor=1.8, frame_rate=7)
                danger_sprite.add(second_danger)
            new_danger = Danger(load_image("FLYING.png", (255, 255, 255)), 4, 1, scale_factor=1.8, frame_rate=7)
            danger_sprite.add(new_danger)

        player_animation.update()
        danger_sprite.update()

        for goomba in danger_sprite:
            if player_animation.rect.colliderect(goomba.rect):
                if player_animation.rect.bottom - player_animation.speed_y < goomba.rect.top:
                    count_sound.play()
                    goomba.kill()
                    player_animation.speed_y = -JUMP_HEIGHT // 2  # Отскок вверх
                    COUNT += 1
                    print(COUNT)
                else:
                    pygame.mixer_music.stop()
                    player_animation.kill()
                    if not player_animation.player_out:
                        die_sound.play(0)
                    player_animation.player_out = True
        if player_animation.player_out:
            pass
        #твой экран

        screen.fill(BLACK)
        player_sprite.draw(screen)
        danger_sprite.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


