import arcade

# Константы
from constants import *


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Хитбокс игрока
        hitbox = arcade.load_texture("Sprites/player_hitbox.png")
        self.texture = hitbox

        # Расположение игрока
        self.center_x = PLAYER_START_X
        self.center_y = PLAYER_START_Y
        self.direction = 'right'

        # Характеристики
        self.speed = MOVE_SPEED
        self.scale = 1.67

        # Переменные
        self.movement = 0
        self.dash_timer = 0
        self.dash_reset_timer = 0

        self.DASHING = False


    def update(self, dt: float):
        self.change_x = self.movement

        # В какую сторону смотрит
        if self.movement > 0:
            self.direction = 'right'
        elif self.movement < 0:
            self.direction = 'left'

        if not self.DASHING:
            self.dash_reset_timer += dt

    def dash(self, dt: float):
        self.dash_timer += dt

        if self.direction == 'right':
            self.center_x += DASH_SPEED
        elif self.direction == 'left':
            self.center_x -= DASH_SPEED