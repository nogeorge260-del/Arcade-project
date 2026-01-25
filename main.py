import arcade

# Константы
from constants import *

# Механики
from player import Player


class Game(arcade.Window):
    #def __init__(self, width, height, title):
    def __init__(self):
        super().__init__(fullscreen=FULLSCREEN)
        arcade.set_background_color(arcade.color.BLACK)

        # Камера
        self.world_camera = arcade.camera.Camera2D()
        self.set_caption(GAME_NAME)

        # Размеры мира
        self.world_width = 10000
        self.world_height = 10000

    def setup(self):
        # Игрок
        self.player = Player()

        # Карта
        self.tile_map = arcade.load_tilemap("Tile Maps/test_location_2.json", scaling=2)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Задача/Сброс переменных
        self.jump_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS

        self.keys = []

        self.old_cam_pos_x, self.old_cam_pos_y = self.world_camera.position

        # Физика
        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            platforms=self.scene["Platforms"],
        )

        # Текстура игрока
        self.player_texture = arcade.Sprite("Sprites/placeholder player texture.jpeg", scale=1.35)
        self.player_texture.center_x = self.player.center_x
        self.player_texture.center_y = self.player.center_y

        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player_texture)

        # Фон
        self.bg = arcade.Sprite("Sprites/background placeholder.jpg", scale=1.5)
        self.bg.center_x = 768
        self.bg.center_y = 768
        self.bg_spritelist = arcade.SpriteList()
        self.bg_spritelist.append(self.bg)

    def on_draw(self):
        self.clear()

        self.bg_spritelist.draw()

        self.world_camera.use()
        self.player_spritelist.draw()
        self.scene.draw()

    def on_update(self, dt: float):
        # Обновления камеры
        cam_x, cam_y = self.world_camera.position
        dz_left = cam_x - DEAD_ZONE_W // 2
        dz_right = cam_x + DEAD_ZONE_W // 2
        dz_bottom = cam_y - DEAD_ZONE_H // 2
        dz_top = cam_y + DEAD_ZONE_H // 2

        px, py = self.player.center_x, self.player.center_y
        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + DEAD_ZONE_W // 2
        elif px > dz_right:
            target_x = px - DEAD_ZONE_W // 2
        if py < dz_bottom:
            target_y = py + DEAD_ZONE_H // 2
        elif py > dz_top:
            target_y = py - DEAD_ZONE_H // 2

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(self.world_width - half_w, target_x))
        target_y = max(half_h, min(self.world_height - half_h, target_y))

        smooth_x = (1 - CAMERA_SMOOTHNESS) * cam_x + CAMERA_SMOOTHNESS * target_x
        smooth_y = (1 - CAMERA_SMOOTHNESS) * cam_y + CAMERA_SMOOTHNESS * target_y
        self.cam_target = (smooth_x, smooth_y)

        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

        # Параллакс
        self.new_cam_pos_x, self.new_cam_pos_y = self.world_camera.position
        if self.old_cam_pos_x != self.new_cam_pos_x:
            self.bg.center_x += (self.new_cam_pos_x - self.old_cam_pos_x) * PARALLAX_SPEED
        if self.old_cam_pos_y != self.new_cam_pos_y:
            self.bg.center_y += (self.new_cam_pos_y - self.old_cam_pos_y) * PARALLAX_SPEED
        self.old_cam_pos_x, self.old_cam_pos_y = self.world_camera.position

        # Движение влево-вправо
        self.player.movement = 0

        if arcade.key.A in self.keys:
            self.player.movement += -self.player.speed
        if arcade.key.D in self.keys:
            self.player.movement += self.player.speed

        self.player.update(dt)
        # Обновление текстуры игрока
        self.player_texture.center_x = self.player.center_x
        self.player_texture.center_y = self.player.center_y

        # Прыжок игрока
        grounded = self.engine.can_jump(y_distance=6)
        if grounded:
            self.time_since_ground = 0
            self.jumps_left = MAX_JUMPS
        else:
            self.time_since_ground += dt

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt

        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)

        if want_jump:
            can_coyote = (self.time_since_ground <= COYOTE_TIME)
            if grounded or can_coyote:
                self.engine.jump(JUMP_SPEED)
                self.jump_buffer_timer = 0

        # Рывок
        if (arcade.MOUSE_BUTTON_RIGHT in self.keys or self.player.DASHING) and self.player.dash_reset_timer > (DASH_RESET_TIME):
            self.engine.jump(0)
            self.player.DASHING = True
            self.engine.gravity_constant = 0
            if self.player.dash_timer < DASH_TIME:
                self.player.dash(dt)
            else:
                self.engine.gravity_constant = GRAVITY
                self.player.dash_timer = 0
                self.player.dash_reset_timer = 0
                self.player.DASHING = False

        # Физика лестниц
        on_ladder = self.engine.is_on_ladder()
        if on_ladder:
            # По лестнице вверх/вниз
            if arcade.key.W in self.keys and arcade.key.S not in self.keys:
                self.player.change_y = LADDER_SPEED
            elif arcade.key.W not in self.keys and arcade.key.S in self.keys:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0
            # Обновление текстуры игрока
            self.player_texture.center_x = self.player.center_x
            self.player_texture.center_y = self.player.center_y


        # Коллизия с опасностями
        hit_list = arcade.check_for_collision_with_list(self.player, self.scene["Dangers"])
        if hit_list:
            # Ресет рывка
            self.engine.gravity_constant = GRAVITY
            self.player.dash_timer = 0
            self.player.dash_reset_timer = 0
            self.player.DASHING = False

            # Ресет позиции
            self.player.center_x = 100
            self.player.center_y = 100

        # Обновление физики
        self.engine.update()

    def on_key_press(self, key, modifiers):
        if key in self.keys:
            self.keys.remove(key)
        self.keys.append(key)

        if key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER

    def on_key_release(self, key, modifiers):
        self.keys.remove(key)

        # Вариативная высота прыжка
        if key == arcade.key.SPACE:
            self.jump_pressed = False
            if self.player.change_y > 0:
                self.player.change_y *= 0.45

    def on_mouse_press(self, x, y, button, modifiers):
        self.keys.append(button)
        self.dash_pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        self.keys.remove(button)


def setup_game():
    game = Game()
    game.setup()
    return game


def main():
    setup_game()
    arcade.run()


if __name__ == "__main__":
    main()