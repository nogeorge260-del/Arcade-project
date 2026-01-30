GAME_NAME = "Cat-O-Head"     # Название игры

FULLSCREEN = True

# Начальные координаты

PLAYER_START_X = 288
PLAYER_START_Y = 512


# Скорость

GRAVITY = 1.75     # Пикс/с^2

MOVE_SPEED = 11.4     # Пикс/с

JUMP_SPEED = 26.5     # Начальный импульс прыжка

LADDER_SPEED = 12.5     # Скрость лазание по лестницам

PARALLAX_SPEED = 0.7     # Скорость параллакса

DASH_SPEED = 36.9     # Скорость ускорения
DASH_TIME = 9 / 60     # Время ускорения
DASH_RESET_TIME = 20 / 60


# Камера

CAMERA_SMOOTHNESS = .09     # Плавность камеры

DEAD_ZONE_W = 15
DEAD_ZONE_H = 15


# QOL

COYOTE_TIME = 0.08     # Сколько после схода с платформы можно ещё прыгнуть

JUMP_BUFFER = 0.02     # Баффер прыжка

MAX_JUMPS = 1     # Кол-во прыжков за раз
