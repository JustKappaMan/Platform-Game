from sys import exit
from math import ceil
from pathlib import Path
from random import randint

import pygame as pg

from settings import *


class Sky:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.surf = pg.Surface(screen.get_size())
        self.surf.fill(pg.color.Color('skyblue'))
        self.surf_pos = (0, 0)

    def render(self):
        self.screen.blit(self.surf, self.surf_pos)


class Ground:
    def __init__(self, screen: pg.Surface, surf: pg.Surface):
        self.screen = screen
        self.surf = surf
        self.surfs_count = ceil(screen.get_width() / surf.get_width())

        match round(screen.get_height() / self.surf.get_height()):
            case 2:
                self.surf_y_pos = screen.get_height() - surf.get_height() // 4
            case 3:
                self.surf_y_pos = screen.get_height() - surf.get_height() // 2
            case _:
                self.surf_y_pos = screen.get_height() - surf.get_height()

    def render(self):
        for i in range(self.surfs_count):
            self.screen.blit(self.surf, (i * self.surf.get_width(), self.surf_y_pos))


class FPSCounter:
    def __init__(self, screen: pg.Surface, clock: pg.time.Clock):
        self.screen = screen
        self.clock = clock
        self.font = pg.font.SysFont('Arial', 16, bold=True)
        self.color = pg.color.Color('red')
        self.position = (screen.get_width() - 8, 8)
        self.fps = None
        self.surf = None
        self.rect = None

    def render(self):
        self.fps = f'{int(self.clock.get_fps())}'
        self.surf = self.font.render(self.fps, True, self.color)
        self.rect = self.surf.get_rect(topright=self.position)
        self.screen.blit(self.surf, self.rect)


class ScoreCounter:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.font = pg.font.SysFont('Arial', 16, bold=True)
        self.color = pg.color.Color('darkgreen')
        self.position = (8, 8)
        self.start_score = 0
        self.current_score = 0
        self.score_divisor = 100
        self.surf = None
        self.rect = None

    def render(self):
        self.current_score = pg.time.get_ticks() // self.score_divisor - self.start_score
        self.surf = self.font.render(f'Score: {self.current_score}', True, self.color)
        self.rect = self.surf.get_rect(topleft=self.position)
        self.screen.blit(self.surf, self.rect)

    def refresh(self):
        self.start_score = pg.time.get_ticks() // self.score_divisor


class StartScreen:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.background_color = pg.color.Color('darkgreen')
        self.font = pg.font.SysFont('Arial', 32, bold=True)
        self.font_surf = self.font.render('Press Space to run', True, pg.color.Color('yellow'))
        self.font_rect = self.font_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    def render(self):
        self.screen.fill(self.background_color)
        self.screen.blit(self.font_surf, self.font_rect)


class GameOverScreen:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.background_color = pg.color.Color('red')
        self.font = pg.font.SysFont('Arial', 32, bold=True)
        self.font_surf = self.font.render('Game Over', True, pg.color.Color('yellow'))
        self.font_rect = self.font_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    def render(self):
        self.screen.fill(self.background_color)
        self.screen.blit(self.font_surf, self.font_rect)


def main():
    pg.init()
    pg.display.set_caption('Simple Game')
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()

    game_is_active = False

    sky = Sky(screen)
    ground = Ground(screen, pg.image.load(Path('graphics', 'ground.png')).convert())

    player_surf = pg.image.load(Path('graphics', 'player.png')).convert()
    player_rect = player_surf.get_rect(midbottom=(64, ground.surf_y_pos))
    player_gravity = 0

    running_enemy_surf = pg.image.load(Path('graphics', 'running_enemy.png')).convert()
    flying_enemy_surf = pg.image.load(Path('graphics', 'flying_enemy.png')).convert()
    enemies_rects = []

    fps_counter = FPSCounter(screen, clock)
    score_counter = ScoreCounter(screen)
    start_screen = StartScreen(screen)
    game_over_screen = GameOverScreen(screen)

    enemy_timer = pg.USEREVENT + 1
    pg.time.set_timer(enemy_timer, 1800)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                exit()

            if game_is_active:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE and player_rect.bottom >= ground.surf_y_pos:
                        player_gravity = -22
                if event.type == enemy_timer:
                    if randint(0, 2):
                        enemies_rects.append(running_enemy_surf.get_rect(midbottom=(
                            randint(screen.get_width() + 256, screen.get_width() + 512), ground.surf_y_pos)))
                    else:
                        enemies_rects.append(flying_enemy_surf.get_rect(midbottom=(
                            randint(screen.get_width() + 256, screen.get_width() + 512), ground.surf_y_pos - 64)))
            else:
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    enemies_rects.clear()
                    score_counter.refresh()
                    player_gravity = 0
                    player_rect.midbottom = (64, ground.surf_y_pos)
                    game_is_active = True

        if game_is_active:
            sky.render()
            ground.render()

            player_gravity += 1
            player_rect.y += player_gravity
            if player_rect.bottom >= ground.surf_y_pos:
                player_rect.bottom = ground.surf_y_pos
            screen.blit(player_surf, player_rect)

            if enemies_rects:
                for enemy_rect in enemies_rects:
                    if enemy_rect.colliderect(player_rect):
                        game_is_active = False

                    enemy_rect.x -= 4

                    if enemy_rect.bottom == ground.surf_y_pos:
                        screen.blit(running_enemy_surf, enemy_rect)
                    else:
                        screen.blit(flying_enemy_surf, enemy_rect)

                enemies_rects = [enemy_rect for enemy_rect in enemies_rects if enemy_rect.x > -enemy_rect.width]

            fps_counter.render()
            score_counter.render()
        else:
            if score_counter.current_score == 0:
                start_screen.render()
            else:
                game_over_screen.render()

        pg.display.update()
        clock.tick(MAX_FRAMERATE)


if __name__ == '__main__':
    main()
