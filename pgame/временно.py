import pygame as pg


def main():
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((640, 480))
    font = pg.font.Font(None, 64)
    orig_surf = font.render('Enter your text', True, pg.Color('royalblue'))
    txt_surf = orig_surf.copy()
    alpha = 255  # The current alpha value of the surface.
    timer = 20  # To get a 20 frame delay.

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        if timer > 0:
            timer -= 1
        else:
            if alpha > 0:
                # Reduce alpha each frame, but make sure it doesn't get below 0.
                alpha = max(0, alpha-4)
                # Create a copy so that the original surface doesn't get modified.
                txt_surf = orig_surf.copy()
                txt_surf.fill((255, 255, 255, alpha), special_flags=pg.BLEND_RGBA_MULT)

        screen.fill((30, 30, 30))
        screen.blit(txt_surf, (30, 60))
        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    main()
    pg.quit()