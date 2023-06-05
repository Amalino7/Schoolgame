import arcade
from constants import *
from typing import Optional
class PlayerSprite(arcade.Sprite):
    """ Player Sprite """
    def __init__(self,
                item_list: arcade.SpriteList,
                hit_box_algorithm):
        """ Init """
        self.physics_engine = Optional[arcade.PymunkPhysicsEngine]
        self.attack_cooldown = 0
        # Let parent initialize
        super().__init__()

        # Set our scale
        self.scale = SPRITE_SCALING_PLAYER
        main_path = "other_assets\magus\magus"
        
        self.front_texture_list=[]
        self.back_texture_list=[]
        self.left_texture_list=[]
        self.right_texture_list=[]
        self.HP = 10
        # Load textures for idle standing\
        for i in range(1,3):
            self.front_texture_list.append(arcade.load_texture(f"{main_path}_front_{i}.png",hit_box_algorithm=hit_box_algorithm))
            self.back_texture_list.append(arcade.load_texture(f"{main_path}_back_{i}.png"))
            self.left_texture_list.append(arcade.load_texture(f"{main_path}_left_{i}.png"))
            self.right_texture_list.append(arcade.load_texture(f"{main_path}_right_{i}.png"))

        # Set the initial texture
        self.texture = self.front_texture_list[0]

        self.is_trying_to_take_object=False
        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points

        # Default to face-right
        self.character_face_direction_1 = RIGHT_FACING
        self.character_face_direction_2 = FRONT_FACING
        # Index of our current texture
        self.cur_texture = 0

        # How far have we traveled horizontally and vertically since changing the texture
        self.x_odometer = 0
        self.y_odometer = 0

        self.item_list=item_list
        # self.ladder_list = ladder_list
        self.is_on_ladder = False
        self.score = 0

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        """ Handle being moved by the pymunk engine """
        itemhitlist=arcade.check_for_collision_with_list(self,self.item_list)
        if len(itemhitlist)>0:
            if self.is_trying_to_take_object==True:
                for i in itemhitlist:
                    self.score+=10
                    i.remove_from_sprite_lists()

        # Figure out if we need to face left or right
        #Reminder fix this bs later
        if dx < -DEAD_ZONE and self.character_face_direction_1 == RIGHT_FACING:
            self.character_face_direction_1 = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction_1 == LEFT_FACING:
            self.character_face_direction_1 = RIGHT_FACING

        if dy > DEAD_ZONE and self.character_face_direction_2 == FRONT_FACING:
            self.character_face_direction_2 = BACK_FACING
        elif dy < -DEAD_ZONE and self.character_face_direction_2 == BACK_FACING:
            self.character_face_direction_2 = FRONT_FACING
        # Add to the odometer how far we've moved
        self.x_odometer += dx
        self.y_odometer += dy

        # Idle animation
        if abs(dx) <= DEAD_ZONE and abs(dy) <= DEAD_ZONE:
            self.texture = self.front_texture_list[0]
            return
        # Have we moved far enough to change the texture?
        if abs(dx)>abs(dy):
            if abs(self.x_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
            # Reset the odometer
                self.x_odometer = 0

                # Advance the walking animation
                self.cur_texture += 1
                if self.cur_texture > 1:
                    self.cur_texture = 0
                if self.character_face_direction_1 == LEFT_FACING:
                    self.texture = self.left_texture_list[self.cur_texture]
                elif self.character_face_direction_1 == RIGHT_FACING:
                    self.texture = self.right_texture_list[self.cur_texture]
        elif abs(dy)>abs(dx):
            if abs(self.y_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
                self.y_odometer = 0

                # Advance the walking animation
                self.cur_texture += 1
                if self.cur_texture > 1:
                    self.cur_texture = 0
                
                if self.character_face_direction_2 == FRONT_FACING:
                    self.texture = self.front_texture_list[self.cur_texture]
                elif self.character_face_direction_2 == BACK_FACING:
                    self.texture = self.back_texture_list[self.cur_texture]