import arcade
import random  # для будущих рандомов

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Телепорт Платформер"
PLAYER_MOVE_SPEED = 5
PLAYER_JUMP_SPEED = 18
GRAVITY = 0.8
CAMERA_DECAY = 0.4


# Простая lerp функция
def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


# Данные уровней — платформы теперь с (cx, cy, w, h), используем изображение, растягиваем
level_data = [
    {
        'platforms': [
            (640, 50, 1280, 100),
            (300, 150, 200, 32),
            (900, 250, 200, 32),
        ],
        'goal': (1100, 280)
    },
    {
        'platforms': [
            (640, 50, 1280, 100),
            (200, 200, 150, 32), (500, 300, 150, 32), (900, 200, 150, 32), (1200, 350, 150, 32),
        ],
        'goal': (1250, 380)
    },
    {
        'platforms': [
            (640, 50, 1280, 100),
            (100, 400, 150, 32), (400, 250, 150, 32), (800, 450, 150, 32), (1100, 300, 150, 32),
        ],
        'goal': (80, 430)
    },
    {
        'platforms': [
            (640, 50, 1280, 100),
            (150, 120, 120, 32), (350, 220, 120, 32), (550, 150, 120, 32),
            (750, 300, 120, 32), (950, 200, 120, 32), (1150, 400, 120, 32),
        ],
        'goal': (1200, 430)
    }
]


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", scale=0.5)
        self.score = 0


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

        self.player_list = arcade.SpriteList()
        self.platforms = arcade.SpriteList()
        self.goal_list = arcade.SpriteList()

        self.player = Player()
        self.player.center_x = 100
        self.player.center_y = 100
        self.player_list.append(self.player)

        self.left_pressed = False
        self.right_pressed = False
        self.current_level = 0  # Перенёс сюда, перед load_level

        self.load_level()

        self.score_text = None
        self.update_score()

    def load_level(self):
        data = level_data[self.current_level]

        self.platforms.clear()

        for cx, cy, w, h in data['platforms']:
            plat = arcade.Sprite(":resources:images/tiles/boxCrate_double.png")  # используем встроенное изображение
            plat.center_x = cx
            plat.center_y = cy
            plat.width = w  # растягиваем по ширине
            plat.height = h  # растягиваем по высоте
            self.platforms.append(plat)

        gx, gy = data['goal']
        self.goal = arcade.Sprite(":resources:images/items/star.png", scale=0.5)
        self.goal.center_x = gx
        self.goal.center_y = gy
        self.goal_list.clear()
        self.goal_list.append(self.goal)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.platforms, GRAVITY
        )

    def next_level(self):
        px, py = self.player.position

        self.current_level = (self.current_level + 1) % len(level_data)
        self.load_level()

        self.player.center_x = px
        self.player.center_y = py
        self.player.change_x = 0
        self.player.change_y = 0

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.platforms, GRAVITY
        )

        self.player.score += 1
        self.update_score()

    def update_score(self):
        self.score_text = arcade.Text(
            f"Уровни пройдено: {self.player.score}", 10, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 24
        )

    def on_draw(self):
        self.clear()

        self.camera.activate()
        self.platforms.draw()
        self.player_list.draw()
        self.goal_list.draw()

        self.gui_camera.activate()
        self.score_text.draw()

    def on_update(self, delta_time):
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_MOVE_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = PLAYER_MOVE_SPEED
        else:
            self.player.change_x = 0

        self.physics_engine.update()

        if arcade.check_for_collision(self.player, self.goal):
            self.next_level()

        self.update_camera()

    def update_camera(self):
        camera_target_x = self.player.center_x - (SCREEN_WIDTH / 2)
        camera_target_y = self.player.center_y - (SCREEN_HEIGHT / 2)

        current_pos = self.camera.position

        new_x = lerp(current_pos[0], camera_target_x, CAMERA_DECAY)
        new_y = lerp(current_pos[1], camera_target_y, CAMERA_DECAY)
        self.camera.position = new_x, new_y

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right_pressed = False


def main():
    window = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()