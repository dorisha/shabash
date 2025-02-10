import random

import pygame
import sys
import os

pygame.init()
pygame.mixer.init()
BLACK = (0, 0, 0)
SIZE = width, height = 800, 800
FPS = 60
PLAYER_SPEED = 10  # Уменьшена скорость персонажа
WHITE = (255, 255, 255)
ground = 685   # уровень земли
JUMP_HEIGHT = 25  # сила прыжка
GRAVITY = 1  # сила гравитации
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Персонаж")
all_sprites = pygame.sprite.Group()  # создаем глобальную группу всех спрайтов
player_sprite = pygame.sprite.Group()
danger_sprite = pygame.sprite.Group()
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

font_path = 'PanterA.ttf'
font_large = pygame.font.Font(font_path, 48)
font_small = pygame.font.Font(font_path, 24)
font = pygame.font.Font('PanterA.ttf', 120)
font_but = pygame.font.Font('PanterA.ttf', 97)
play_but = (300, 500, 230, 120)
character_but = (240, 390, 340, 120)

game_over = False
retry_text = font_small.render('YOU DIED', True, (255, 255, 255))
retry_rect = retry_text.get_rect()
retry_rect.midtop = (width // 2, height // 2)


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


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (width, height))


def draw_button(text, x, y, width, height, picture):
    image = load_image(picture, color_key=-1)
    image = pygame.transform.scale(image, (width, height))
    text_surf = font_but.render(text, True, 'white')
    screen.blit(image, (x, y))
    screen.blit(text_surf, (x + 55, y + 40))


if __name__ == '__main__':
    # Загрузка спрайт-листа для анимации
    player_animation = Player(load_image("Owlet_Monster_Run_6.png"), 6, 1, scale_factor=1.8, frame_rate=7)
    all_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    danger_sprite = pygame.sprite.Group()

    player_sprite.add(player_animation)
    all_sprites.add(player_animation)
    # Уменьшаем размер и скорость анимации
    text_surface = font.render('Shabash', True, (255, 255, 255))
    clock = pygame.time.Clock()
    BackGround_m = Background('data/стратовый фон.jpg')
    last_spawn_time = pygame.time.get_ticks()
    running_m = True
    INIT_DELAY = 2000
    while running_m:
        screen.fill([255, 255, 255])
        screen.blit(BackGround_m.image, BackGround_m.rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_m = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if play_but[0] <= mouse_x <= play_but[0] + play_but[2] and play_but[1] <= mouse_y <= play_but[3] + \
                        play_but[1]:
                    BackGround = Background('data/фон.png')
                    grass = Background('data/трава.png')
                    running = True
                    score = 5
                    while running:
                        screen.fill([255, 255, 255])
                        screen.blit(BackGround.image, BackGround.rect)
                        screen.blit(grass.image, grass.rect)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                pygame.mixer.music.stop()

                        # Получаем нажатые клавиши
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_LEFT]:
                            player_animation.move(-PLAYER_SPEED)  # движение влево
                            player_animation.facing_left = True  # Устанавливаем флаг для зеркалирования
                            player_animation.is_moving = True  # Устанавливаем флаг движения
                        elif keys[pygame.K_RIGHT]:
                            player_animation.move(PLAYER_SPEED)  # движение вправо
                            player_animation.facing_left = False  # Сбрасываем флаг зеркалирования
                            player_animation.is_moving = True  # Устанавливаем флаг движения
                        else:
                            player_animation.is_moving = False  # Персонаж стоит, прекращаем анимацию

                        if keys[pygame.K_UP]:
                            player_animation.jump()  # прыжок

                        now = pygame.time.get_ticks()
                        if now - last_spawn_time > INIT_DELAY:
                            last_spawn_time = now
                            if COUNT > 10:
                                third_danger = Danger2(load_image("Skeleton_01_Yellow_Walk (1).png", (255, 255, 255)),
                                                       10, 1, scale_factor=1.8, frame_rate=7)
                                danger_sprite.add(third_danger)
                            if COUNT > 5:
                                second_danger = Danger1(load_image("NightBorne.png", (255, 255, 255)), 6, 1,
                                                        scale_factor=1.8, frame_rate=7)
                                danger_sprite.add(second_danger)
                            new_danger = Danger(load_image("FLYING.png", (255, 255, 255)), 4, 1, scale_factor=1.8,
                                                frame_rate=7)
                            if not player_animation.player_out:
                                danger_sprite.add(new_danger)

                        score_text = font_but.render((str(COUNT)), True, (255, 255, 255))
                        score_rect = score_text.get_rect()

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
                            image = load_image('смерть.jpg')
                            image = pygame.transform.scale(image, (800, 800))
                            screen.blit(image, (0, 0))
                            score_rect.midbottom = (width // 2, height // 2)
                            screen.blit(retry_text, retry_rect)

                        #     # Обновление состояния игрок
                        score_rect.midtop = (width // 2, 5)
                        player_sprite.draw(screen)
                        danger_sprite.draw(screen)
                        screen.blit(score_text, score_rect)
                        pygame.display.flip()
        screen.blit(text_surface, (225, 650))  # Обновление дисплея
        draw_button("play", play_but[0], play_but[1], play_but[2], play_but[3], 'кнопка главная.png')
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
