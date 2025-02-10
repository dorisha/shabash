import os

import pygame


pygame.init()
SIZE = width, height = 800, 800
screen = pygame.display.set_mode(SIZE)
font_path = 'data/ofont.ru_Wolgadeutsche.ttf'
font_name = pygame.font.Font(font_path, 48)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
FPS = 60


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


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (width, height))


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
        self.speed_x = 0
        self.facing_left = True
        self.player_out = True
        self.rect.x = 400
        self.rect.y = 400

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
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.frame_timer = 0



if __name__ == '__main__':
    new_danger_spisok = pygame.sprite.Group()
    BackGround_m = Background('data/img.png')
    running_m = True
    text = 'Pink'
    text_evil = font_name.render('Злодеи', True, (255, 255, 255))
    text_hero = font_name.render('Герои', True, (255, 255, 255))
    new_danger = Danger(load_image("FLYING.png", color_key=-1), 4, 1, scale_factor=1.8, frame_rate=7)
    new_danger_spisok.add(new_danger)
    while running_m:
        text_surface = font_name.render(text, True, (80, 0, 100))
        name_rect = (140, 310)
        screen.fill([255, 255, 255])
        screen.blit(BackGround_m.image, BackGround_m.rect)
        image_p = load_image('Pink.стоит.png', color_key=-1)
        image_d = load_image('Dude.стоит.png', color_key=-1)
        image_o = load_image('Owlet.стоит.png', color_key=-1)
        image_F = load_image('FLYING.png', color_key=-1)
        image_sk = load_image('Скилет.png', color_key=-1)
        image_n = load_image('ниндзя.jpg', color_key=-1)
        image_svitok = load_image('свиток.dark.png', color_key=-1)
        image_p = pygame.transform.scale(image_p, (50, 50))
        image_d = pygame.transform.scale(image_d, (50, 50))
        image_o = pygame.transform.scale(image_o, (50, 50))
        image_F = pygame.transform.scale(image_F, (50, 50))
        image_sk = pygame.transform.scale(image_sk, (50, 50))
        image_n = pygame.transform.scale(image_n, (50, 50))
        image_svitok = pygame.transform.scale(image_svitok, (300, 400))
        screen.blit(image_p, (700, 420))
        screen.blit(image_d, (700, 500))
        screen.blit(image_o, (700, 580))
        screen.blit(image_F, (700, 160))
        screen.blit(image_sk, (700, 240))
        screen.blit(image_n, (700, 320))
        screen.blit(image_svitok, (30, 260))
        screen.blit(text_surface, name_rect)
        screen.blit(text_evil, (640, 100))
        screen.blit(text_hero, (650, 360))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_m = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 700 <= mouse_x <= 750 and 420 <= mouse_y <= 470:
                    text = 'Pink'
                elif 700 <= mouse_x <= 750 and 500 <= mouse_y <= 550:
                    text = 'а'
                elif 700 <= mouse_x <= 750 and 580 <= mouse_y <= 630:
                    text = 'Бяша'
                elif 700 <= mouse_x <= 750 and 160 <= mouse_y <= 210:
                    text = 'в'
                elif 700 <= mouse_x <= 750 and 240 <= mouse_y <= 630:
                    text = 'о'
                elif 700 <= mouse_x <= 750 and 320 <= mouse_y <= 630:
                    text = 'х'
        new_danger_spisok.update()
        new_danger_spisok.draw(screen)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
