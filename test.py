"""
Example of Pymunk Physics Engine Platformer
"""
import math
from typing import Optional
import arcade
import os
from Player import *
from constants import *

class BulletSprite(arcade.SpriteSolidColor):
    """ Bullet Sprite """
    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """ Handle when the sprite is moved by the physics engine. """
        # If the bullet falls below the screen, remove it
        if self.center_y < -100:
            self.remove_from_sprite_lists()
    

class Button():
    def __init__(self, sprite1,sprite2):
        self.sprite1=sprite1
        self.sprite2=sprite2
    # super().__init__(
    #         ":resources:images/tiles/boxCrate_double.png",
    #         center_x=x,
    #         center_y=y
    #     )
        self.mainsprite=sprite1
        self.pressed = False
def drawButtons(buttonlist):
    for button in buttonlist:
        button.mainsprite.draw()
class Door():
    def __init__(self,Spritelist):
        self.spritelist=Spritelist
        self.state = 0 #closed
def drawDoors(doorlist):
    for door in doorlist:
        if door.state == 0:
            door.spritelist.draw()

class Money(arcade.Sprite):
    value = 30
class GameWindow(arcade.Window):
    """ Main Window """

    def __init__(self, width, height, title):
        """ Create the variables """

        # Init the parent class
        super().__init__(width, height, title)
        self.set_fullscreen()
        # Player sprite
        self.player_sprite: Optional[PlayerSprite] = None
        self.level = 1 #level
        self.end_of_map = 0  #indicate endpoint
        # Sprite lists we need
        self.background: Optional[arcade.SpriteList] = None
        self.end_points: Optional[arcade.SpriteList] = None
        self.player_list: Optional[arcade.SpriteList] = None
        self.wall_list: Optional[arcade.SpriteList] = None
        self.bullet_list: Optional[arcade.SpriteList] = None
        self.item_list: Optional[arcade.SpriteList] = None
        self.moving_sprites_list: Optional[arcade.SpriteList] = None
        self.ladder_list: Optional[arcade.SpriteList] = None
        self.pushable_objects_list: Optional[arcade.SpriteList] = None
        self.door_list = None
        self.is_trying_to_take_object: bool=False
        self.button_list=None
        self.gui_camera = None
        # Track the current state of what key is pressed
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False
        self.respawn_index=0
        #add scene
        self.scene: arcade.Scene() = None
        # self.possible_jumps=2
        self.camera=None
        # Physics engine
        self.physics_engine: Optional[arcade.PymunkPhysicsEngine] = None
        self.spawn_point=None
        self.player_sprite_old=None
        self.mode = 0 #shoot
        self.impersonating = False
        # Set background color
        arcade.set_background_color(arcade.color.AMAZON)


    def setup(self):
        """ Set up everything with the game """
        # Map name
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        cwd=os.getcwd()
        map_name = f"{cwd}\TIledproject\hmm.json"
        map_name = r'{}'.format(map_name)
        # map_name = ":resources:/tiled_maps/pymunk_test_map.json"

        # Load in TileMap
        tile_map = arcade.load_tilemap(map_name, SPRITE_SCALING_TILES)
        
        # Pull the sprite layers out of the tile map
        self.wall_list = tile_map.sprite_lists["Platforms"]
        self.pushable_objects_list = tile_map.sprite_lists["Pushable Items"]
        self.item_list = tile_map.sprite_lists["Dynamic Items"]
        self.ladder_list = tile_map.sprite_lists["Ladders"]
        self.moving_sprites_list = tile_map.sprite_lists['Moving Platforms']
        self.background = tile_map.sprite_lists['Background']
        self.door_list = []
        
        i=0
        while True:
            try:
                self.door_list.append(Door(tile_map.sprite_lists[f"Door{i+1}"]))
                print("door added",flush=1)
                i+=1
            except:
                break

        self.end_points = tile_map.sprite_lists["Despawn"]
        self.spawn_point = tile_map.object_lists["Spawn"][self.respawn_index]
        self.button_list = []
        i=0
        while True:
            try:
                for button1,button2 in zip(tile_map.sprite_lists[f"B{i+1}State1"],tile_map.sprite_lists[f"B{i+1}State2"]):
                    self.button_list.append(Button(button1,button2))
                print("door added",flush=1)
                i+=1
            except:
                break

        # print(self.button_list,flush=True)
        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # self.button1 = Button(1600, 1000)
        # self.button2 = Button(300, 1200)
        # self.button_list.append(self.button1)
        # self.button_list.append(self.button2)

        # self.spawn_points = tile_map.get_tilemap_layer("Spawn")#spawn point

        self.camera=arcade.Camera(self.width,self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        # Create player sprite
        self.player_sprite = PlayerSprite(self.item_list, hit_box_algorithm="Detailed")

        # Set player location
        
        self.player_sprite.center_x = self.spawn_point.shape[0]
        self.player_sprite.center_y=self.spawn_point.shape[1]
        # Add to player sprite list
        self.player_list.append(self.player_sprite)

        # --- Pymunk Physics Engine Setup ---

        # The default damping for every object controls the percent of velocity
        # the object will keep each second. A value of 1.0 is no speed loss,
        # 0.9 is 10% per second, 0.1 is 90% per second.
        # For top-down games, this is basically the friction for moving objects.
        # For platformers with gravity, this should probably be set to 1.0.
        # Default value is 1.0 if not specified.
        damping = DEFAULT_DAMPING

        # Set the gravity. (0, 0) is good for outer space and top-down.
        gravity = (0, -0)

        # Create the physics engine
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=damping,
                                                         gravity=gravity,)
        
        self.physics_engine.add_sprite_list(self.pushable_objects_list,
                                            friction=0.7,
                                            collision_type="push",
                                            moment_of_intertia=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                            body_type=arcade.PymunkPhysicsEngine.DYNAMIC)

        def item_hit_by_player_handler(player_sprite, item_sprite, _arbiter, _space, _data):
            if self.is_trying_to_take_object==True:
                item_sprite.remove_from_sprite_lists()
                print("shit taken")
        self.physics_engine.add_collision_handler("player1","item",post_handler=item_hit_by_player_handler)

        def reached_end_point(player_sprite, end_sprite, _arbiter, _space, _data):
            self.respawn_index+=1
            if self.respawn_index>=2:
                self.respawn_index=0
            self.setup()
        self.physics_engine.add_collision_handler("player1","end",post_handler=reached_end_point)

        # self.physics_engine.
        def wall_hit_handler(bullet_sprite, _wall_sprite, _arbiter, _space, _data):
            """ Called for bullet/wall collision """
            bullet_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler("bullet", "wall", post_handler=wall_hit_handler)
        self.physics_engine.add_collision_handler("bullet", "end", post_handler=wall_hit_handler)

        def push_hit_handler(bullet_sprite, push_sprite, _arbiter, _space, _data):
            if self.mode == 1:
                self.player_sprite_old = self.player_sprite
                self.player_sprite = push_sprite   
                self.impersonating = True
            bullet_sprite.remove_from_sprite_lists()
        self.physics_engine.add_collision_handler("bullet", "push", post_handler=push_hit_handler)

        def item_hit_handler(bullet_sprite, item_sprite, _arbiter, _space, _data):
            """ Called for bullet/wall collision """
            bullet_sprite.remove_from_sprite_lists()
            item_sprite.remove_from_sprite_lists()

        self.physics_engine.add_collision_handler("bullet", "item", post_handler=item_hit_handler)

        # Add the player.
        # For the player, we set the damping to a lower value, which increases
        # the damping rate. This prevents the character from traveling too far
        # after the player lets off the movement keys.
        # Setting the moment to PymunkPhysicsEngine.MOMENT_INF prevents it from
        # rotating.
        # Friction normally goes between 0 (no friction) and 1.0 (high friction)
        # Friction is between two objects in contact. It is important to remember
        # in top-down games that friction moving along the 'floor' is controlled
        # by damping.
        self.physics_engine.add_sprite_list(self.end_points,mass=1,collision_type="end", body_type = arcade.PymunkPhysicsEngine.STATIC)
        self.physics_engine.add_sprite(self.player_sprite,
                                    #    friction=PLAYER_FRICTION,
                                       mass=PLAYER_MASS,
                                       moment=arcade.PymunkPhysicsEngine.MOMENT_INF,
                                       collision_type="player1",
                                       elasticity=1,
                                       max_horizontal_velocity=PLAYER_MAX_HORIZONTAL_SPEED,
                                       max_vertical_velocity=PLAYER_MAX_VERTICAL_SPEED)

        # Create the walls.
        # By setting the body type to PymunkPhysicsEngine.STATIC the walls can't
        # move.
        # Movable objects that respond to forces are PymunkPhysicsEngine.DYNAMIC
        # PymunkPhysicsEngine.KINEMATIC objects will move, but are assumed to be
        # repositioned by code and don't respond to physics forces.
        # Dynamic is default.
        self.physics_engine.add_sprite_list(self.wall_list,
                                            # friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        

        for door in self.door_list:
            self.physics_engine.add_sprite_list(door.spritelist,
                                            # friction=WALL_FRICTION,
                                            collision_type="wall",
                                            body_type=arcade.PymunkPhysicsEngine.STATIC)
        # Add kinematic sprites
        self.physics_engine.add_sprite_list(self.moving_sprites_list,
                                            body_type=arcade.PymunkPhysicsEngine.KINEMATIC)
        
    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        #Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.E:
            self.player_sprite.is_trying_to_take_object=True
            self.is_trying_to_take_object=True

        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True


        if key == arcade.key.Q:
            if self.mode == 0:
                self.mode = 1
            else:
                self.mode = 0

        if key == arcade.key.ESCAPE and self.mode == 1:
            self.player_sprite=self.player_sprite_old
    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.E:
            self.is_trying_to_take_object=False
            self.player_sprite.is_trying_to_take_object=False
        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called whenever the mouse button is clicked. """
        if self.impersonating == True:
            return
        bullet = BulletSprite(20, 5, arcade.color.LIGHT_BLUE)
        self.bullet_list.append(bullet)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.position = self.player_sprite.position

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x+self.camera.position.x
        dest_y = y+self.camera.position.y
        
        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # What is the 1/2 size of this sprite, so we can figure out how far
        # away to spawn the bullet
        size = max(self.player_sprite.width, self.player_sprite.height) / 2

        # Use angle to to spawn bullet away from player in proper direction
        bullet.center_x += size * math.cos(angle)
        bullet.center_y += size * math.sin(angle)

        # Set angle of bullet
        bullet.angle = math.degrees(angle)

        # Gravity to use for the bullet
        # If we don't use custom gravity, bullet drops too fast, or we have
        # to make it go too fast.
        # Force is in relation to bullet's angle.
        # bullet_gravity = (0, -BULLET_GRAVITY)

        # Add the sprite. This needs to be done AFTER setting the fields above.
        self.physics_engine.add_sprite(bullet,
                                       mass=BULLET_MASS,
                                       damping=1,
                                       collision_type="bullet",
                                       gravity=(0,0),
                                       elasticity=0.9)

        # Add force to bullet
        force = (BULLET_MOVE_FORCE, 0)
        self.physics_engine.apply_force(bullet, force)

    def on_update(self, delta_time):
        """ Movement and game logic """

    # Button logic
        for i in self.button_list:
            for j in self.pushable_objects_list:
                if self.player_sprite.collides_with_sprite(i.mainsprite) or j.collides_with_sprite(i.mainsprite):
                    i.pressed = True
                    i.mainsprite=i.sprite2

                elif not i.sprite1.collides_with_list(self.pushable_objects_list):
                    i.pressed = False
                    i.mainsprite=i.sprite1


        # Door/Button logic
        """dswfisdjslfjsofls"""
        for i in self.button_list:
            try:
                curdoor=self.door_list[self.button_list.index(i)]
            except:
                continue
            if i.pressed == False and curdoor.state == 1:
                curdoor.state = 0
                self.physics_engine.add_sprite_list(curdoor.spritelist,
                                                # friction=WALL_FRICTION,
                                                collision_type="wall",
                                                body_type=arcade.PymunkPhysicsEngine.STATIC)
            elif i.pressed == True and curdoor.state == 0:
               curdoor.state = 1
               for sprite in curdoor.spritelist:
                self.physics_engine.remove_sprite(sprite)


        # is_on_ground = self.physics_engine.is_on_ground(self.player_sprite)
        # Update player forces based on keys pressed
        if self.left_pressed and not self.right_pressed:
            force = (-PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.right_pressed and not self.left_pressed:
            # Create a force to the right. Apply it.
            force = (PLAYER_MOVE_FORCE_ON_GROUND, 0)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 1.0)
            
        if self.up_pressed and not self.down_pressed:
            force = (0, PLAYER_MOVE_FORCE_ON_GROUND)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)
        elif self.down_pressed and not self.up_pressed:
            force = (0, -PLAYER_MOVE_FORCE_ON_GROUND)
            self.physics_engine.apply_force(self.player_sprite, force)
            # Set friction to zero for the player while moving
            self.physics_engine.set_friction(self.player_sprite, 0)

        else:
            # Player's feet are not moving. Therefore up the friction so we stop.
            self.physics_engine.set_friction(self.player_sprite, 1.0)

        # Move items in the physics engine
        self.physics_engine.step()

        # For each moving sprite, see if we've reached a boundary and need to
        # reverse course.
        for moving_sprite in self.moving_sprites_list:
            if moving_sprite.boundary_right and \
                    moving_sprite.change_x > 0 and \
                    moving_sprite.right > moving_sprite.boundary_right:
                moving_sprite.change_x *= -1
            elif moving_sprite.boundary_left and \
                    moving_sprite.change_x < 0 and \
                    moving_sprite.left > moving_sprite.boundary_left:
                moving_sprite.change_x *= -1
            if moving_sprite.boundary_top and \
                    moving_sprite.change_y > 0 and \
                    moving_sprite.top > moving_sprite.boundary_top:
                moving_sprite.change_y *= -1
            elif moving_sprite.boundary_bottom and \
                    moving_sprite.change_y < 0 and \
                    moving_sprite.bottom < moving_sprite.boundary_bottom:
                moving_sprite.change_y *= -1

            # Figure out and set our moving platform velocity.
            # Pymunk uses velocity is in pixels per second. If we instead have
            # pixels per frame, we need to convert.
            velocity = (moving_sprite.change_x * 1 / delta_time, moving_sprite.change_y * 1 / delta_time)
            self.physics_engine.set_velocity(moving_sprite, velocity)
        
        self.center_camera_to_player()
        

    def on_draw(self):
        """ Draw everything """
        self.clear()
        self.camera.use()
        self.background.draw()
        drawButtons(self.button_list)
        self.wall_list.draw()
        self.pushable_objects_list.draw()
        # self.ladder_list.draw()
        self.moving_sprites_list.draw()
        self.bullet_list.draw()
        self.item_list.draw()
        self.player_list.draw()

        self.end_points.draw_hit_boxes()
        self.item_list.draw_hit_boxes()
        self.pushable_objects_list.draw_hit_boxes()
        self.player_list.draw_hit_boxes()
        drawDoors(self.door_list)

        self.gui_camera.use()
        if self.impersonating == True:
            score_text = f"Score: {self.player_sprite_old.score} Mode is {self.mode}"
        else:
            score_text = f"Score: {self.player_sprite.score} Mode is {self.mode}"
        arcade.draw_text(
            score_text,
            30,
            50,
            arcade.csscolor.WHITE,
            18,
       )
def main():
    """ Main function """
    window = GameWindow(SCREEN_WIDTH-30, SCREEN_HEIGHT-30, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()