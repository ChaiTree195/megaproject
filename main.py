import arcade
import math


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Телепорт Платформер"

GRAVITY = 0.7
DASH_SPEED = 20
DASH_DURATION = 0.10
PLAYER_MOVE_SPEED = 7
PLAYER_JUMP_SPEED = 12
JUMP_HOLD_FORCE = 0.20
COYOTE_TIME = 0.12
JUMP_BUFFER_TIME = 0.12


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=0.5
        )
        self.score = 0


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.EERIE_BLACK)

        self.player_list = arcade.SpriteList()
        self.platforms = arcade.SpriteList()
        self.death_list = arcade.SpriteList()
        self.bkg_list = arcade.SpriteList()
        self.bkg2_list = arcade.SpriteList()
        self.goal_list = arcade.SpriteList()

        self.player = Player()
        self.player_list.append(self.player)

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.dash_remaining_time = 0.0
        self.can_dash = True
        self.was_on_ground = False
        self.dash_dir_x = 0.0
        self.dash_dir_y = 0.0

        self.jump_hold_pressed = False
        self.coyote_time_left = 0.0
        self.jump_buffer_time = 0.0

        self.tile_map = None

        self.load_level("levelstart.tmx")

        self.score_text = None
        self.update_score()

    def get_dash_direction(self):
        dx = 0.0
        dy = 0.0
        if self.right_pressed:
            dx += 1.0
        if self.left_pressed:
            dx -= 1.0
        if self.up_pressed:
            dy += 1.0
        if self.down_pressed:
            dy -= 1.0

        length = math.sqrt(dx ** 2 + dy ** 2)
        if length == 0:
            return None

        return dx / length, dy / length

    def load_level(self, tmx_file="levelstart.tmx"):
        self.tile_map = arcade.load_tilemap(tmx_file, scaling=1)

        self.platforms = self.tile_map.sprite_lists.get("WALLS", arcade.SpriteList())
        self.death_list = self.tile_map.sprite_lists.get("DEATH", arcade.SpriteList())
        self.bkg_list = self.tile_map.sprite_lists.get("BKG", arcade.SpriteList())
        self.bkg2_list = self.tile_map.sprite_lists.get("BKG2", arcade.SpriteList())

        self.goal_list.clear()
        if "GOAL" in self.tile_map.object_lists:
            goal_obj = self.tile_map.object_lists["GOAL"][0]
            self.goal = arcade.Sprite(":resources:images/items/star.png", scale=0.3)
            self.goal.center_x = goal_obj.x + goal_obj.width / 2
            self.goal.center_y = goal_obj.y + goal_obj.height / 2
            self.goal_list.append(self.goal)

        # Спавн
        tw = self.tile_map.tile_width
        th = self.tile_map.tile_height
        map_height_px = self.tile_map.height * th

        tile_x = 10
        tile_y = 4

        self.player.center_x = tile_x * tw + tw / 2
        self.player.center_y = map_height_px - (tile_y * th + th / 2)

        for plat in self.platforms:
            plat.friction = 1.2
        self.player.friction = 0.4

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.platforms, GRAVITY
        )

        self.center_world()

    def center_world(self):
        map_width = self.tile_map.width * self.tile_map.tile_width
        map_height = self.tile_map.height * self.tile_map.tile_height

        offset_x = (SCREEN_WIDTH - map_width) / 2
        offset_y = (SCREEN_HEIGHT - map_height) / 2

        for sprite_list in [
            self.platforms,
            self.death_list,
            self.bkg_list,
            self.bkg2_list,
            self.goal_list,
        ]:
            for spr in sprite_list:
                spr.center_x += offset_x
                spr.center_y += offset_y

        self.player.center_x += offset_x
        self.player.center_y += offset_y

    def update_score(self):
        self.score_text = arcade.Text(
            f"Уровни пройдено: {self.player.score}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            24
        )

    def on_draw(self):
        self.clear()
        self.bkg2_list.draw()
        self.bkg_list.draw()
        self.platforms.draw()
        self.death_list.draw()
        self.player_list.draw()
        self.goal_list.draw()
        self.score_text.draw()

    def on_update(self, delta_time):
        if self.dash_remaining_time > 0:
            self.player.change_x = DASH_SPEED * self.dash_dir_x
            self.player.change_y = DASH_SPEED * self.dash_dir_y
            self.dash_remaining_time -= delta_time
        else:
            if self.left_pressed and not self.right_pressed:
                self.player.change_x = -PLAYER_MOVE_SPEED
            elif self.right_pressed and not self.left_pressed:
                self.player.change_x = PLAYER_MOVE_SPEED
            else:
                self.player.change_x = 0

        self.jump_buffer_time = max(0, self.jump_buffer_time - delta_time)

        if self.jump_hold_pressed and self.player.change_y > 0:
            self.player.change_y += JUMP_HOLD_FORCE

        self.physics_engine.update()

        on_ground_now = self.physics_engine.can_jump(y_distance=10)
        if not self.was_on_ground and on_ground_now:
            self.can_dash = True
        self.was_on_ground = on_ground_now

        if on_ground_now:
            self.coyote_time_left = COYOTE_TIME
        self.coyote_time_left = max(0, self.coyote_time_left - delta_time)

        if self.jump_buffer_time > 0 and (on_ground_now or self.coyote_time_left > 0):
            self.player.change_y = PLAYER_JUMP_SPEED
            self.jump_buffer_time = 0
            self.coyote_time_left = 0

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = True
            self.jump_hold_pressed = True
            self.jump_buffer_time = JUMP_BUFFER_TIME
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = True
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = True
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = True
        elif key == arcade.key.Z:
            direction = self.get_dash_direction()
            if direction and self.can_dash:
                self.dash_dir_x, self.dash_dir_y = direction
                self.dash_remaining_time = DASH_DURATION
                self.can_dash = False

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.W, arcade.key.UP):
            self.up_pressed = False
            self.jump_hold_pressed = False
        elif key in (arcade.key.S, arcade.key.DOWN):
            self.down_pressed = False
        elif key in (arcade.key.A, arcade.key.LEFT):
            self.left_pressed = False
        elif key in (arcade.key.D, arcade.key.RIGHT):
            self.right_pressed = False


def main():
    window = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
