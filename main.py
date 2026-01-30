import arcade
from arcade.gl import RGBA_INTEGER
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

        self.tile_map4 = arcade.load_tilemap("Tile Maps/final.json", scaling=2, use_spatial_hash=True)
        self.final = arcade.Scene.from_tilemap(self.tile_map4)

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
        self.old_grounded = True
        self.respawn_timer = 0
        self.respawning = False
        self.switching1 = False
        self.switching2 = False
        self.switching3 = False
        self.switch_timer = 0
        self.not_switching = False
        self.amount = 0
        self.keys1 = False
        self.keys2 = False
        self.keys3 = False
        self.keys4 = False
        self.uselessc2 = True
        self.win = False

        # SFX
        self.fall = arcade.load_sound('SFX/fall.mp3')
        self.dash = arcade.load_sound('SFX/dash.mp3')
        self.key = arcade.load_sound('SFX/key_picked_up.mp3')
        self.door = arcade.load_sound('SFX/door.mp3')
        self.background_song = arcade.load_sound('SFX/Songs/these streets once brimmed with life.mp3')

        # Физика
        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            platforms=(self.tutorial["Platforms"], self.tutorial["Doors 1"]),
        )

        # Текстура игрока
        self.player_texture = arcade.Sprite("Sprites/sprites/cat-o-head.png", scale=3.25)
        self.player_texture.center_x = self.player.center_x
        self.player_texture.center_y = self.player.center_y

        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player_texture)

        # Hello Kitty
        self.kitty = arcade.Sprite("Sprites/sprites/final_hero.png", scale=.5)
        self.kitty.center_x = 2688
        self.kitty.center_y = 256
        self.kitty_spritelist = arcade.SpriteList()
        self.kitty_spritelist.append(self.kitty)

        # Фон
        self.bg = arcade.Sprite("Sprites/sprites/crystal_bg.png", scale=50)
        self.bg.center_x = 1512
        self.bg.center_y = 800
        self.bg_spritelist = arcade.SpriteList()
        self.bg_spritelist.append(self.bg)

        # Animation
        self.goleft = arcade.Sprite("Sprites/sprites/walking_cat_Left1.png", scale=3.25)
        self.goright = arcade.Sprite("Sprites/sprites/walking_cat_Right1.png", scale=3.25)
        self.left_list = arcade.SpriteList()
        self.left_list.append(self.goleft)
        self.right_list = arcade.SpriteList()
        self.right_list.append(self.goright)

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
        self.bg_music = self.background_song.play(loop=True, volume=.33)

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
            if not self.respawning:
                if not self.player.WALKING:
                    self.player_spritelist.draw()
                else:
                    if self.player.direction == 'right':
                        self.right_list.draw()
                    else:
                        self.left_list.draw()
            if self.map == 0:
                self.tutorial["Deco"].draw()
            elif self.map == 1:
                self.location1["Deco"].draw()
            elif self.map == 2:
                self.location2["Deco"].draw()
                self.location2["decodoor"].draw()
                cx, cy = self.world_camera.position
                arcade.Text(f'Собрано ключей: {self.amount}/4', x=cx - 900, y=cy + 450, font_size=40,
                            color=arcade.color.WHITE, anchor_x='left').draw()
                if not self.keys1:
                    self.location2["keydeco1"].draw()
                if not self.keys2:
                    self.location2["keydeco2"].draw()
                if not self.keys3:
                    self.location2["keydeco3"].draw()
                if not self.keys4:
                    self.location2["keydeco4"].draw()
            elif self.map == 3:
                self.final["Deco"].draw()
                self.kitty_spritelist.draw()

        else:
            self.manager.draw()

        if (self.switching1 or self.switching2) and not self.not_switching:
            draw_x, draw_y = self.world_camera.position
            arcade.draw_circle_filled(draw_x, draw_y, 2000, (0, 0, 0, 255 * self.switch_timer))
        elif self.not_switching:
            draw_x, draw_y = self.world_camera.position
            if 2 - self.switch_timer > 0 and self.switch_timer != 0:
                arcade.draw_circle_filled(draw_x, draw_y, 2000, (0, 0, 0, 255 * (2 - self.switch_timer)))

        if self.jump_help:
            cx, cy = self.world_camera.position
            arcade.Text('Нажмите "Пробел" для прыжка', x=cx-800, y=cy-500, font_size=50,
                        color=arcade.color.WHITE, anchor_x='left').draw()
        if self.dash_help:
            cx, cy = self.world_camera.position
            arcade.Text('Нажмите "ПКМ" для рывка', x=cx-800, y=cy-500, font_size=50,
                        color=arcade.color.WHITE, anchor_x='left').draw()

        if self.win:
            cx, cy = self.world_camera.position
            arcade.Text('Вы выиграли! Вы спасли Hello Kitty!', x=cx, y=cy, font_size=75,
                        color=arcade.color.WHITE, anchor_x='center').draw()


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
            if (self.player.center_x >= 3712 and self.map == 0) or self.switching1:
                self.player.can_move = False
                self.switching1 = True
                self.switch_timer += dt
                if self.switch_timer >= 1 and not self.not_switching:
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

                    self.player.can_move = True
                    self.switch_timer += dt
                    self.not_switching = True

                if self.switch_timer >= 2:
                    self.switch_timer = 0
                    self.switching1 = False
                    self.player.can_move = True
                    self.not_switching = False


            # Смена 1 локации на 2
            if (self.player.center_y >= 3136 and self.map == 1) or self.switching2:
                self.player.can_move = False
                self.switching2 = True
                self.switch_timer += dt
                if self.switch_timer >= 1 and not self.not_switching:
                    self.map = 2
                    self.location1["Platforms"].move(0, -10000)
                    self.location1["Dangers"].move(0, -10000)
                    self.location1["Checkpoints"].move(0, -10000)
                    self.location1["Doors"].move(0, -10000)
                    self.engine.platforms = (self.location2["Platforms"], self.location2["Doors"])
                    self.player.center_x = 1216
                    self.player.center_y = 384
                    self.last_checkpoint = [1216, 384]
                    self.world_width = 4864
                    self.world_height = 3328

                    self.player.can_move = True
                    self.switch_timer += dt
                    self.not_switching = True

                if self.switch_timer >= 2:
                    self.switch_timer = 0
                    self.switching2 = False
                    self.player.can_move = True
                    self.not_switching = False


            # Смена 2 локации на final
            if (self.player.center_y >= 3328 and self.map == 2) or self.switching3:
                self.player.can_move = False
                self.switching3 = True
                self.switch_timer += dt
                if self.switch_timer >= 1 and not self.not_switching:
                    self.map = 3
                    self.location2["Platforms"].move(0, -10000)
                    self.location2["Dangers"].move(0, -10000)
                    self.location2["Checkpoints"].move(0, -10000)
                    self.location2["Doors"].move(0, -10000)
                    self.engine.platforms = self.final["Platforms"]
                    self.player.center_x = 896
                    self.player.center_y = 384
                    self.last_checkpoint = [896, 384]
                    self.world_width = 10000
                    self.world_height = 10000

                    self.player.can_move = True
                    self.switch_timer += dt
                    self.not_switching = True

                if self.switch_timer >= 2:
                    self.switch_timer = 0
                    self.switching3 = False
                    self.player.can_move = True
                    self.not_switching = False


            # Обновления камеры
            if not self.respawning:
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
                if hit_list or self.respawning:
                    self.player.can_move = False
                    self.respawning = True
                    self.respawn_timer += dt
                    if self.respawn_timer >= 0.33:
                        # Ресет рывка
                        self.engine.gravity_constant = GRAVITY
                        self.player.dash_timer = 0
                        self.player.dash_reset_timer = 0
                        self.player.DASHING = False

                        # Ресет позиции
                        self.player.center_x = self.last_checkpoint[0]
                        self.player.center_y = self.last_checkpoint[1]

                        self.respawning = False
                        self.respawn_timer = 0
                        self.player.can_move = True


                # Коллизия с чекпоинтами
                hit_list = arcade.check_for_collision_with_list(self.player, self.tutorial["Checkpoints"])
                if hit_list:
                    self.last_checkpoint = [self.player.center_x, self.player.center_y]

            if self.map == 1:
                hit_list = arcade.check_for_collision_with_list(self.player, self.location1["Dangers"])
                if hit_list or self.respawning:
                    self.player.can_move = False
                    self.respawning = True
                    self.respawn_timer += dt
                    if self.respawn_timer >= 0.5:
                        # Ресет рывка
                        self.engine.gravity_constant = GRAVITY
                        self.player.dash_timer = 0
                        self.player.dash_reset_timer = 0
                        self.player.DASHING = False

                        # Ресет позиции
                        self.player.center_x = self.last_checkpoint[0]
                        self.player.center_y = self.last_checkpoint[1]

                        self.respawning = False
                        self.respawn_timer = 0
                        self.player.can_move = True

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

            if self.map == 2:
                hit_list = arcade.check_for_collision_with_list(self.player, self.location2["Dangers"])
                if hit_list or self.respawning:
                    self.player.can_move = False
                    self.respawning = True
                    self.respawn_timer += dt
                    if self.respawn_timer >= 0.5:
                        # Ресет рывка
                        self.engine.gravity_constant = GRAVITY
                        self.player.dash_timer = 0
                        self.player.dash_reset_timer = 0
                        self.player.DASHING = False

                        # Ресет позиции
                        self.player.center_x = self.last_checkpoint[0]
                        self.player.center_y = self.last_checkpoint[1]

                        self.respawning = False
                        self.respawn_timer = 0
                        self.player.can_move = True


                # Коллизия с чекпоинтами
                hit_list = arcade.check_for_collision_with_list(self.player, self.location2["Checkpoints"])
                if hit_list:
                    self.last_checkpoint = [self.player.center_x, self.player.center_y]

                # Собранные ключи
                hit_list = arcade.check_for_collision_with_list(self.player, self.location2["Keys1"])
                if hit_list and not self.keys1:
                    arcade.play_sound(self.key, volume=.5, speed=1.)
                    self.amount += 1
                    self.keys1 = True
                hit_list = arcade.check_for_collision_with_list(self.player, self.location2["Keys2"])
                if hit_list and not self.keys2:
                    arcade.play_sound(self.key, volume=.5, speed=1.)
                    self.amount += 1
                    self.keys2 = True
                hit_list = arcade.check_for_collision_with_list(self.player, self.location2["Keys3"])
                if hit_list and not self.keys3:
                    arcade.play_sound(self.key, volume=.5, speed=1.)
                    self.amount += 1
                    self.keys3 = True
                hit_list = arcade.check_for_collision_with_list(self.player, self.location2["Keys4"])
                if hit_list and not self.keys4:
                    arcade.play_sound(self.key, volume=.5, speed=1.)
                    self.amount += 1
                    self.keys4 = True

            if self.map == 3:
                hit_list = arcade.check_for_collision_with_list(self.player, self.final["Win"])
                if hit_list:
                    self.win = True
                    self.player.can_move = False

            # Движение влево-вправо
            self.player.movement = 0

            if not self.player.DASHING:
                if arcade.key.A in self.keys:
                    self.player.movement += -self.player.speed
                    self.player.WALKING = True
                else:
                    self.player.WALKING = False
                if arcade.key.D in self.keys:
                    self.player.movement += self.player.speed
                    self.player.WALKING = True
                else:
                    self.player.WALKING = False

            self.player.update(dt)
            # Обновление текстуры игрока
            self.player_texture.center_x = self.player.center_x
            self.player_texture.center_y = self.player.center_y
            self.goleft.center_x = self.player.center_x
            self.goleft.center_y = self.player.center_y
            self.goright.center_x = self.player.center_x
            self.goright.center_y = self.player.center_y

            # Прыжок игрока
            grounded = self.engine.can_jump(y_distance=6)

            if not self.old_grounded and grounded and self.time_since_ground >= (40 / 60):
                arcade.play_sound(self.fall, volume=.1, speed=1.5)
            self.old_grounded = grounded

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

            # Рывок (dash)
            if self.player.can_dash:
                if (arcade.MOUSE_BUTTON_RIGHT in self.keys or self.player.DASHING) and self.player.dash_reset_timer > (DASH_RESET_TIME):
                    self.engine.jump(0)
                    self.player.DASHING = True
                    self.engine.gravity_constant = 0
                    if self.player.dash_timer == 0:
                        arcade.play_sound(self.dash, volume=.5, speed=1.25)
                    if self.player.dash_timer < DASH_TIME:
                        self.player.dash(dt)
                    else:
                        self.engine.gravity_constant = GRAVITY
                        self.player.dash_timer = 0
                        self.player.dash_reset_timer = 0
                        self.player.DASHING = False

            # Если все ключи собраны
            if self.keys1 and self.keys2 and self.keys3 and self.keys4 and self.uselessc2:
                self.uselessc2 = False
                self.location2["Doors"].move(320, 0)
                self.location2["decodoor"].move(320, 0)
                arcade.play_sound(self.door, volume=.5, speed=1.)

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
