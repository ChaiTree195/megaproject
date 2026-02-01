import arcade
from PIL import Image

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "KORObKA"
GRAVITY = 0.7
PLAYER_MOVE_SPEED = 4
PLAYER_JUMP_SPEED = 7
JUMP_HOLD_FORCE = 0.20
COYOTE_TIME = 0.12
JUMP_BUFFER_TIME = 0.12
HEADER_HEIGHT = 50
ANIMATION_SPEED = 0.1
SPRITE_SHEET = "character_sheet.png"
SPRITE_WIDTH = 16
SPRITE_HEIGHT = 16
PLAYER_SCALE = 2.5

class Player(arcade.AnimatedWalkingSprite):
    def __init__(self):
        super().__init__(scale=PLAYER_SCALE)
        self.score = 0
        self.facing_direction = "right"
        self.jump_textures = []
        self.jump_left_textures = []
        self.jump_texture_time = 0.0
        self.cur_jump_texture_index = 0
        sheet_image = Image.open(SPRITE_SHEET)
        cropped = sheet_image.crop((0, 304, SPRITE_WIDTH, SPRITE_HEIGHT + 304))
        self.stand_right_textures.append(arcade.Texture(name="stand_right_0", image=cropped))
        cropped = sheet_image.crop((16, 304, SPRITE_WIDTH + 16, SPRITE_HEIGHT + 304))
        self.stand_right_textures.append(arcade.Texture(name="stand_right_1", image=cropped))
        for i, tex in enumerate(self.stand_right_textures):
            flipped_image = tex.image.transpose(Image.FLIP_LEFT_RIGHT)
            self.stand_left_textures.append(arcade.Texture(name=f"stand_left_{i}", image=flipped_image))
        cropped = sheet_image.crop((0, 320, SPRITE_WIDTH, SPRITE_HEIGHT+320))
        self.walk_right_textures.append(arcade.Texture(name="walk_right_0", image=cropped))
        cropped = sheet_image.crop((16, 320, SPRITE_WIDTH+16, SPRITE_HEIGHT+320))
        self.walk_right_textures.append(arcade.Texture(name="walk_right_1", image=cropped))
        cropped = sheet_image.crop((32, 320, SPRITE_WIDTH+32, SPRITE_HEIGHT+320))
        self.walk_right_textures.append(arcade.Texture(name="walk_right_1", image=cropped))
        cropped = sheet_image.crop((48, 320, SPRITE_WIDTH+48, SPRITE_HEIGHT+320))
        self.walk_right_textures.append(arcade.Texture(name="walk_right_1", image=cropped))
        for i, tex in enumerate(self.walk_right_textures):
            flipped_image = tex.image.transpose(Image.FLIP_LEFT_RIGHT)
            self.walk_left_textures.append(arcade.Texture(name=f"walk_left_{i}", image=flipped_image))
        cropped = sheet_image.crop((0, 320, SPRITE_WIDTH, SPRITE_HEIGHT+320))
        self.jump_textures.append(arcade.Texture(name="jump_right_0", image=cropped))
        cropped = sheet_image.crop((16, 320, SPRITE_WIDTH+16, SPRITE_HEIGHT+320))
        self.jump_textures.append(arcade.Texture(name="jump_right_1", image=cropped))
        for i, tex in enumerate(self.jump_textures):
            flipped_image = tex.image.transpose(Image.FLIP_LEFT_RIGHT)
            self.jump_left_textures.append(arcade.Texture(name=f"jump_left_{i}", image=flipped_image))
        self.texture = self.stand_right_textures[0]

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x < 0:
            self.facing_direction = "left"
        elif self.change_x > 0:
            self.facing_direction = "right"
        if self.change_y != 0:
            self.jump_texture_time += delta_time
            if self.jump_texture_time > ANIMATION_SPEED:
                self.jump_texture_time -= ANIMATION_SPEED
                self.cur_jump_texture_index = (self.cur_jump_texture_index + 1) % len(self.jump_textures)
            if self.facing_direction == "left":
                self.texture = self.jump_left_textures[self.cur_jump_texture_index]
            else:
                self.texture = self.jump_textures[self.cur_jump_texture_index]
            return
        self.jump_texture_time = 0.0
        self.cur_jump_texture_index = 0
        super().update_animation(delta_time)

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.background = arcade.load_texture("background.png")
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
        self.jump_hold_pressed = False
        self.coyote_time_left = 0.0
        self.jump_buffer_time = 0.0
        self.max_air_jumps = 1
        self.air_jumps_remaining = self.max_air_jumps
        self.tile_map = None
        self.scale_factor = 1.0
        self.gravity_scaled = GRAVITY
        self.player_move_speed_scaled = PLAYER_MOVE_SPEED
        self.player_jump_speed_scaled = PLAYER_JUMP_SPEED
        self.jump_hold_force_scaled = JUMP_HOLD_FORCE
        self.ground_check_distance = 10
        self.current_level = 1
        self.fading_out = False
        self.fading_in = False
        self.fade_time = 0.0
        self.fade_duration = 0.5
        self.level_transition = False
        self.respawn_needed = False
        self.timer = 10.0
        self.timer_text = None
        self.score_text = None
        self.load_level()
        self.update_score()

    def load_level(self):
        if self.current_level == 1:
            tmx_file = "levelstart.tmx"
        else:
            tmx_file = f"level{self.current_level}.tmx"
        self.tile_map = arcade.load_tilemap(tmx_file, scaling=1)
        self.platforms = self.tile_map.sprite_lists.get("WALLS", arcade.SpriteList())
        self.death_list = self.tile_map.sprite_lists.get("DEATH", arcade.SpriteList())
        self.bkg_list = self.tile_map.sprite_lists.get("BKG", arcade.SpriteList())
        self.bkg2_list = self.tile_map.sprite_lists.get("BKG2", arcade.SpriteList())
        self.goal_list = self.tile_map.sprite_lists.get("GOAL", arcade.SpriteList())
        self.spawn_list = self.tile_map.sprite_lists.get("SPAWN", arcade.SpriteList())
        tw = self.tile_map.tile_width
        th = self.tile_map.tile_height
        map_width_px = self.tile_map.width * tw
        map_height_px = self.tile_map.height * th
        effective_height = SCREEN_HEIGHT - HEADER_HEIGHT
        scale_x = SCREEN_WIDTH / map_width_px
        scale_y = effective_height / map_height_px
        self.scale_factor = min(scale_x, scale_y)
        self.gravity_scaled = GRAVITY * self.scale_factor
        self.player_move_speed_scaled = PLAYER_MOVE_SPEED * self.scale_factor
        self.player_jump_speed_scaled = PLAYER_JUMP_SPEED * self.scale_factor
        self.jump_hold_force_scaled = JUMP_HOLD_FORCE * self.scale_factor
        self.ground_check_distance = 10 * self.scale_factor
        all_lists = [
            self.platforms, self.death_list, self.bkg_list, self.bkg2_list,
            self.goal_list
        ]
        for sprite_list in all_lists:
            for spr in sprite_list:
                spr.scale_x *= self.scale_factor
                spr.scale_y *= self.scale_factor
                spr.center_x *= self.scale_factor
                spr.center_y *= self.scale_factor
                spr.alpha = 0 if self.fading_in else 255
        if self.spawn_list:
            for spr in self.spawn_list:
                spr.scale_x *= self.scale_factor
                spr.scale_y *= self.scale_factor
                spr.center_x *= self.scale_factor
                spr.center_y *= self.scale_factor
                spr.alpha = 0  # Not displayed
            spawn_sprite = self.spawn_list[0]
            self.spawn_x = spawn_sprite.center_x
            self.spawn_y = spawn_sprite.center_y
        else:
            # Fallback for level 1 hardcoded, others default to bottom-left-ish
            tile_x = 4
            tile_y = 10
            self.spawn_x = (tile_x * tw + tw / 2) * self.scale_factor
            self.spawn_y = (map_height_px - (tile_y * th + th / 2)) * self.scale_factor
        for plat in self.platforms:
            plat.friction = 1.2
        self.player.friction = 0.4
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.platforms, self.gravity_scaled
        )
        self.timer = 1000.0
        self.timer_text = arcade.Text(
            f"Время: {int(self.timer)}",
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            24
        )
        self.center_world()
        offset_x = (SCREEN_WIDTH - map_width_px * self.scale_factor) / 2
        offset_y = (effective_height - map_height_px * self.scale_factor) / 2
        self.spawn_x += offset_x
        self.spawn_y += offset_y
        self.player.center_x = self.spawn_x
        self.player.center_y = self.spawn_y
        self.player.alpha = 0 if self.fading_in else 255

    def center_world(self):
        map_width_px = self.tile_map.width * self.tile_map.tile_width
        map_height_px = self.tile_map.height * self.tile_map.tile_height
        effective_height = SCREEN_HEIGHT - HEADER_HEIGHT
        map_width_scaled = map_width_px * self.scale_factor
        map_height_scaled = map_height_px * self.scale_factor
        offset_x = (SCREEN_WIDTH - map_width_scaled) / 2
        offset_y = (effective_height - map_height_scaled) / 2
        all_lists = [
            self.platforms, self.death_list, self.bkg_list, self.bkg2_list,
            self.goal_list
        ]
        for sprite_list in all_lists:
            for spr in sprite_list:
                spr.center_x += offset_x
                spr.center_y += offset_y

    def update_score(self):
        self.score_text = arcade.Text(
            f"Уровни пройдено: {self.player.score}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            24
        )

    def respawn(self):
        self.player.center_x = self.spawn_x
        self.player.center_y = self.spawn_y
        self.player.change_x = 0
        self.player.change_y = 0
        self.air_jumps_remaining = self.max_air_jumps
        self.coyote_time_left = 0.0
        self.jump_buffer_time = 0.0

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                SCREEN_WIDTH * 1.5,
                SCREEN_HEIGHT * 1.5
            )
        )
        self.bkg2_list.draw(pixelated=True)
        self.bkg_list.draw(pixelated=True)
        self.platforms.draw(pixelated=True)
        self.death_list.draw(pixelated=True)
        self.player_list.draw()
        self.goal_list.draw(pixelated=True)
        self.score_text.draw()
        self.timer_text.draw()

    def on_update(self, delta_time):
        if self.fading_out or self.fading_in:
            self.fade_time += delta_time
            if self.fading_out:
                alpha = 255 * (1 - self.fade_time / self.fade_duration)
                if self.fade_time >= self.fade_duration:
                    alpha = 0
                    self.fading_out = False
                    self.fade_time = 0.0
            else:
                alpha = 255 * (self.fade_time / self.fade_duration)
                if self.fade_time >= self.fade_duration:
                    alpha = 255
                    self.fading_in = False
                    self.fade_time = 0.0
            all_lists = [self.platforms, self.death_list, self.bkg_list, self.bkg2_list, self.goal_list, self.player_list]
            for sprite_list in all_lists:
                for spr in sprite_list:
                    spr.alpha = alpha
            return
        if self.level_transition:
            self.level_transition = False
            self.load_level()
            self.fading_in = True
            self.fade_time = 0.0
            self.update_score()
            return
        if self.respawn_needed:
            self.respawn_needed = False
            self.respawn()
            self.fading_in = True
            self.fade_time = 0.0
            return
        self.timer -= delta_time
        self.timer_text.text = f"Время: {int(self.timer)}"
        if self.timer <= 0:
            self.close()
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -self.player_move_speed_scaled
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = self.player_move_speed_scaled
        else:
            self.player.change_x = 0
        self.jump_buffer_time = max(0, self.jump_buffer_time - delta_time)
        if self.jump_hold_pressed and self.player.change_y > 0:
            self.player.change_y += self.jump_hold_force_scaled
        self.physics_engine.update()
        on_ground_now = self.physics_engine.can_jump(y_distance=self.ground_check_distance)
        if on_ground_now:
            self.air_jumps_remaining = self.max_air_jumps
            self.coyote_time_left = COYOTE_TIME
        if not on_ground_now:
            self.coyote_time_left = max(0, self.coyote_time_left - delta_time)
        if self.jump_buffer_time > 0 and (on_ground_now or self.coyote_time_left > 0 or self.air_jumps_remaining > 0):
            self.player.change_y = self.player_jump_speed_scaled
            self.jump_buffer_time = 0
            if not on_ground_now and self.coyote_time_left <= 0:
                self.air_jumps_remaining -= 1
            self.coyote_time_left = 0
        if arcade.check_for_collision_with_list(self.player, self.goal_list):
            if not self.fading_out and not self.level_transition:
                self.player.score += 1
                self.current_level += 1
                if self.current_level > 25:
                    self.close()
                else:
                    self.level_transition = True
                    self.fading_out = True
                    self.fade_time = 0.0
        if arcade.check_for_collision_with_list(self.player, self.death_list):
            if not self.fading_out and not self.respawn_needed:
                self.respawn_needed = True
                self.fading_out = True
                self.fade_time = 0.0
        self.player.update_animation(delta_time)

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