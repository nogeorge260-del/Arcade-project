import arcade

# Константы
from constants import *


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        # Хитбокс игрока
        hitbox = arcade.load_texture("Sprites/player_hitbox.png")
        self.texture = hitbox

        # Расположение игрока по x, y
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
        self.grounded = True
        self.walk_timer = 0
        self.anim_cycle = 0

        self.DASHING = False
        self.WALKING = False
        self.old_walking = False
        self.can_dash = False
        self.can_move = True

        # SFX
        self.walking = arcade.load_sound('SFX/walking.mp3')

    def update(self, dt: float):
        if self.can_move:
            self.change_x = self.movement

            # В какую сторону смотрит
            if self.movement > 0:
                self.direction = 'right'
            elif self.movement <= 0:
                self.direction = 'left'

            if not self.old_walking and self.WALKING:
                self.walking_sfx = self.walking.play(volume=3, speed=1.12, loop=True)
            elif self.old_walking and not self.WALKING:
                arcade.stop_sound(self.walking_sfx)

            self.old_walking = self.WALKING

            if not self.DASHING:
                self.dash_reset_timer += dt

    def dash(self, dt: float):
        if self.can_dash:
            self.dash_timer += dt

            if self.direction == 'right':
                self.center_x += DASH_SPEED
            elif self.direction == 'left':
                self.center_x -= DASH_SPEED
