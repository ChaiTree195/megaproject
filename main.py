import arcade
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "лучший платформер в моей жизни"
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.SKY_BLUE)
        self.player = None
        self.player_list = None
        self.platform_list = None
        self.physics_engine = None
    def setup(self):
        self.platform_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        floor = arcade.SpriteSolidColor(SCREEN_WIDTH, 50, arcade.color.GREEN)
        floor.center_x = SCREEN_WIDTH // 2
        floor.center_y = 25
        self.platform_list.append(floor)
        self.player = arcade.SpriteSolidColor(50, 50, arcade.color.RED)
        self.player.center_x = SCREEN_WIDTH // 2
        self.player.center_y = 100
        self.player_list.append(self.player)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.platform_list,
            gravity_constant=GRAVITY
        )
    def on_draw(self):
        self.clear()
        self.platform_list.draw()
        self.player_list.draw()
    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.UP and self.physics_engine.can_jump():
            self.player.change_y = PLAYER_JUMP_SPEED
    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0
    def on_update(self, delta_time):
        self.physics_engine.update()
        if self.player.top < 0:
            self.player.center_y = 100
            self.player.change_y = 10
            self.player.change_y = 0
def main():
    game = MyGame()
    game.setup()
    arcade.run()
main()