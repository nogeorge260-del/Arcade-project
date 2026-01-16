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

        # Характеристики
        self.speed = MOVE_SPEED
        self.scale = SCALING

        # Переменные
        self.movement = 0


    def update(self, dt: float):
        self.change_x = self.movement