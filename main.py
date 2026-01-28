import arcade
from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

# Константы
from constants import *

# Механики
from player import Player


class Game(arcade.Window):
    def __init__(self):
        super().__init__(fullscreen=FULLSCREEN)
        arcade.set_background_color(arcade.color.BLACK)

        # Камера
        self.world_camera = arcade.camera.Camera2D()
        self.set_caption(GAME_NAME)

        # Размеры мира
        self.world_width = 3776
        self.world_height = 960

    def setup(self):
        # Игрок
        self.player = Player()

        # Локации
        self.tile_map1 = arcade.load_tilemap("Tile Maps/tutorial.json", scaling=2, use_spatial_hash=True)
        self.tutorial = arcade.Scene.from_tilemap(self.tile_map1)

        self.tile_map2 = arcade.load_tilemap("Tile Maps/location1.json", scaling=2, use_spatial_hash=True)
        self.location1 = arcade.Scene.from_tilemap(self.tile_map2)

        self.tile_map3 = arcade.load_tilemap("Tile Maps/location2.json", scaling=2, use_spatial_hash=True)
        self.location2 = arcade.Scene.from_tilemap(self.tile_map3)

        # Задача/Сброс переменных
        self.started = False
        self.starting = False
        self.waiting = False
        self.starting_timer = 0
        self.jump_pressed = False
        self.can_double_jump = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.useless_counter = 0
        self.jumps_left = MAX_JUMPS
        self.keys = []
        self.old_cam_pos_x, self.old_cam_pos_y = self.world_camera.position
        self.door_counter = 0
        self.last_checkpoint = [PLAYER_START_X, PLAYER_START_Y]
        self.advancement_counter = 0
        self.map = 0
        self.jump_help = False
        self.dash_help = False
        self.do_switch1 = False
        self.do_switch2 = False

        # Физика
        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            platforms=(self.tutorial["Platforms"], self.tutorial["Doors 1"]),
        )

        # Текстура игрока
        self.player_texture = arcade.Sprite("Sprites/placeholder player texture.jpeg", scale=1.35)
        self.player_texture.center_x = self.player.center_x
        self.player_texture.center_y = self.player.center_y

        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player_texture)

        # Фон
        self.bg = arcade.Sprite("Sprites/background placeholder.jpg", scale=1.5)
        self.bg.center_x = 1024
        self.bg.center_y = 768
        self.bg_spritelist = arcade.SpriteList()
        self.bg_spritelist.append(self.bg)

        # UI
        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)

        self.setup_widgets()

        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

    def start_game(self):
        self.starting = True
        self.started = True

    def setup_widgets(self):
        # Виджеты
        title = UILabel(text=f'{GAME_NAME}', y=800, font_size=200,
                        text_color=arcade.color.WHITE, width=300, align="center")
        self.box_layout.add(title)

        a = UILabel(text=f' ', y=800, font_size=50,
                        text_color=arcade.color.WHITE, width=300, align="center")
        self.box_layout.add(a)

        start = UIFlatButton(text="Начать Игру", width=400, height=120)
        start.on_click = lambda event: self.start_game()
        self.box_layout.add(start)

        settings = UIFlatButton(text="Настройки", width=400, height=120)
        settings.on_click = lambda event: print('placeholder')
        self.box_layout.add(settings)

        a = UILabel(text=f' ', y=800, font_size=50,
                    text_color=arcade.color.WHITE, width=300, align="center")
        self.box_layout.add(a)

    def on_draw(self):
        self.clear()

        if self.started:
            self.bg_spritelist.draw()

            self.world_camera.use()
            self.player_spritelist.draw()
            if self.map == 0:
                self.tutorial.draw()
            elif self.map == 1:
                self.location1.draw()

        else:
            self.manager.draw()

        if self.jump_help:
            cx, cy = self.world_camera.position
            arcade.Text('Нажмите "Пробел" для прыжка', x=cx-800, y=cy-500, font_size=50,
                        color=arcade.color.WHITE, anchor_x='left').draw()
        if self.dash_help:
            cx, cy = self.world_camera.position
            arcade.Text('Нажмите "ПКМ" для рывка', x=cx-800, y=cy-500, font_size=50,
                        color=arcade.color.WHITE, anchor_x='left').draw()
            print(1)


    def on_update(self, dt: float):
        if self.starting:
            self.starting_timer += dt

        if self.started and not self.waiting:
            # Закрытие двери
            if self.door_counter <= 0.5:
                self.tutorial["Doors 1"].move(0, -384 * dt)
                self.door_counter += dt
            if self.player.center_x > 3500 and self.door_counter <= 1:
                self.tutorial["Doors 1"].move(0, -384 * dt)
                self.door_counter += dt

            # Подсказка о прыжке
            if self.player.center_x > 350 and self.advancement_counter == 0:
                self.jump_help = True
                if arcade.key.SPACE in self.keys:
                    self.jump_help = False
                    self.advancement_counter += 1

            # Подсказка о рывке
            if self.advancement_counter == 1 and self.dash_help:
                if arcade.MOUSE_BUTTON_RIGHT in self.keys:
                    self.dash_help = False
                    self.advancement_counter += 1

            # Смена туториала на 1 локацию
            if (self.player.center_x >= 3712 and self.map == 0) or self.do_switch1:
                self.map = 1
                self.tutorial["Platforms"].move(0, -10000)
                self.tutorial["Dangers"].move(0, -10000)
                self.tutorial["Checkpoints"].move(0, -10000)
                self.tutorial["Doors 1"].move(0, -10000)
                self.engine.platforms = (self.location1["Platforms"], self.location1["Doors"])
                self.player.center_x = 288
                self.player.center_y = 384
                self.last_checkpoint = [288, 384]
                self.world_width = 3840
                self.world_height = 3200

                # Смена 1 локации на 2
                if (self.player.center_y >= 3100 and self.map == 1) or self.do_switch2:
                    self.map = 2
                    self.location1["Platforms"].move(0, -10000)
                    self.location1["Dangers"].move(0, -10000)
                    self.location1["Checkpoints"].move(0, -10000)
                    self.location1["Doors 1"].move(0, -10000)
                    self.engine.platforms = (self.location2["Platforms"], self.location2["Doors"])
                    self.player.center_x = 288
                    self.player.center_y = 384
                    self.last_checkpoint = [288, 384]
                    self.world_width = 3840
                    self.world_height = 3200

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

            # Коллизия
            if self.map == 0:
                hit_list = arcade.check_for_collision_with_list(self.player, self.tutorial["Dangers"])
                if hit_list:
                    # Ресет рывка
                    self.engine.gravity_constant = GRAVITY
                    self.player.dash_timer = 0
                    self.player.dash_reset_timer = 0
                    self.player.DASHING = False

                    # Ресет позиции
                    self.player.center_x = self.last_checkpoint[0]
                    self.player.center_y = self.last_checkpoint[1]

                # Коллизия с чекпоинтами
                hit_list = arcade.check_for_collision_with_list(self.player, self.tutorial["Checkpoints"])
                if hit_list:
                    self.last_checkpoint = [self.player.center_x, self.player.center_y]

            if self.map == 1:
                hit_list = arcade.check_for_collision_with_list(self.player, self.location1["Dangers"])
                if hit_list:
                    # Ресет рывка
                    self.engine.gravity_constant = GRAVITY
                    self.player.dash_timer = 0
                    self.player.dash_reset_timer = 0
                    self.player.DASHING = False

                    # Ресет позиции
                    self.player.center_x = self.last_checkpoint[0]
                    self.player.center_y = self.last_checkpoint[1]

                # Коллизия с чекпоинтами
                hit_list = arcade.check_for_collision_with_list(self.player, self.location1["Checkpoints"])
                if hit_list:
                    self.last_checkpoint = [self.player.center_x, self.player.center_y]

                # Коллизия с чекпоинтами
                hit_list = arcade.check_for_collision_with_list(self.player, self.location1["Dash"])
                if hit_list:
                    self.player.can_dash = True
                    if self.useless_counter == 0:
                        self.useless_counter = 1
                        self.dash_help = True

            # Движение влево-вправо
            self.player.movement = 0

            if not self.player.DASHING:
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
                if grounded or can_coyote or self.can_double_jump:
                    self.engine.jump(JUMP_SPEED)
                    self.jump_buffer_timer = 0

            # Рывок
            if self.player.can_dash:
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