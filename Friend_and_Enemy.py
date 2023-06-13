import arcade
from constants import *
from typing import Optional
import math
from Player import *
import os
class Friend(arcade.Sprite):
    """friend that will follow us arround """
    def __init__(self, main_path, scale, wall_list,player_sprite):
        """Animation"""
        self.cur_texture=0
        super().__init__(scale=scale)
        """Textures"""    
        self.front_texture_list=[]
        self.back_texture_list=[]
        self.left_texture_list=[]
        self.right_texture_list=[]
        # Load textures for idle standing\
        for i in range(1,3):
            self.front_texture_list.append(arcade.load_texture(f"{main_path}_front_{i}.png",hit_box_algorithm="Detailed"))
            self.back_texture_list.append(arcade.load_texture(f"{main_path}_back_{i}.png"))
            self.left_texture_list.append(arcade.load_texture(f"{main_path}_left_{i}.png"))
            self.right_texture_list.append(arcade.load_texture(f"{main_path}_right_{i}.png"))
        #default texture
        self.texture = self.front_texture_list[0]
        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points
        # How far have we traveled horizontally and vertically since changing the texture
        self.x_odometer = 0
        self.y_odometer = 0
        # Default to face-right
        self.character_face_direction_x = RIGHT_FACING
        self.character_face_direction_y = FRONT_FACING

        """Other things"""
        self.barrier_list = arcade.AStarBarrierList(self, wall_list, TILE_SIZE, -16000, 16000, -16000, 16000)
        self.path = None
        self.player_sprite = player_sprite
        self.cur_mode = 1
        self.time_passed = 0
       
    def on_update(self, delta_time: float = 1/60):
        change=self.update_path(self.player_sprite,delta_time)
        self.center_x+=change[0]
        self.center_y+=change[1]
        self.animation(change[0],change[1])
        self.time_passed+=delta_time
        
    def update_path(self, player_sprite,delta_time):
        self.path = arcade.astar_calculate_path(self.position, player_sprite.position, self.barrier_list, diagonal_movement=True)
        change=[0,0]
        # Move to next point on path. Using min to avoid overshooting
        if self.path and len(self.path) > 1:
            if self.center_y < self.path[1][1]:
                change[1] = min(FOLLOW_SPEED, self.path[1][1] - self.center_y)
            elif self.center_y > self.path[1][1]:
                change[1] = -min(FOLLOW_SPEED, self.center_y - self.path[1][1])
            
            if self.center_x < self.path[1][0]:
                change[0] = min(FOLLOW_SPEED, self.path[1][0] - self.center_x)
            elif self.center_x > self.path[1][0]:
                change[0] = -min(FOLLOW_SPEED, self.center_x - self.path[1][0])
        return tuple(change)
    def animation(self,dx,dy):
        # Figure out if we need to face left or right
        #Reminder fix this bs later
        if dx < -DEAD_ZONE and self.character_face_direction_x == RIGHT_FACING:
            self.character_face_direction_x = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction_x == LEFT_FACING:
            self.character_face_direction_x = RIGHT_FACING

        if dy > DEAD_ZONE and self.character_face_direction_y == FRONT_FACING:
            self.character_face_direction_y = BACK_FACING
        elif dy < -DEAD_ZONE and self.character_face_direction_y == BACK_FACING:
            self.character_face_direction_y = FRONT_FACING
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
                if self.character_face_direction_x == LEFT_FACING:
                    self.texture = self.left_texture_list[self.cur_texture]
                elif self.character_face_direction_x == RIGHT_FACING:
                    self.texture = self.right_texture_list[self.cur_texture]
        elif abs(dy)>abs(dx):
            if abs(self.y_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
                self.y_odometer = 0

                # Advance the walking animation
                self.cur_texture += 1
                if self.cur_texture > 1:
                    self.cur_texture = 0
                
                if self.character_face_direction_y == FRONT_FACING:
                    self.texture = self.front_texture_list[self.cur_texture]
                elif self.character_face_direction_y == BACK_FACING:
                    self.texture = self.back_texture_list[self.cur_texture]
class Enemy(arcade.Sprite):
    def __init__(self, main_path, scale,player_sprite,wall_list,path):
        self.cur_texture=0
        self.wall_list=wall_list
        super().__init__(scale=scale)
        """Textures"""    
        self.front_texture_list=[]
        self.back_texture_list=[]
        self.left_texture_list=[]
        self.right_texture_list=[]
        self.HP = 10
        # Load textures for idle standing\
        for i in range(1,3):
            self.front_texture_list.append(arcade.load_texture(f"{main_path}_front_{i}.png",hit_box_algorithm="Detailed"))
            self.back_texture_list.append(arcade.load_texture(f"{main_path}_back_{i}.png"))
            self.left_texture_list.append(arcade.load_texture(f"{main_path}_left_{i}.png"))
            self.right_texture_list.append(arcade.load_texture(f"{main_path}_right_{i}.png"))
        #default texture
        self.texture = self.front_texture_list[0]
        # Hit box will be set based on the first image used.
        self.hit_box = self.texture.hit_box_points
        # How far have we traveled horizontally and vertically since changing the texture
        self.x_odometer = 0
        self.y_odometer = 0
        # Default to face-right
        self.character_face_direction_x = RIGHT_FACING
        self.character_face_direction_y = FRONT_FACING


        """Process path so it scales right"""
        self.static_path = []
        for i in path:
            lista =[]
            for cord in i:
                cord*=SPRITE_SCALING_TILES
                lista.append(cord)
            self.static_path.append(tuple(lista))
        """Path and other things"""
        self.center_x = self.static_path[0][0]
        self.center_y = self.static_path[0][1]
        self.cur_dir=1
        self.player_sprite:Optional[PlayerSprite]=player_sprite
        #self.barrier_list = arcade.AStarBarrierList(self, wall_list, TILE_SIZE, -16000, 16000, -16000, 16000)
        self.time_in_sight = 0
        self.hp = 10
        self.attack_cooldown=0


    def reload(self,physic_engine:Optional[arcade.PymunkPhysicsEngine]):
        physic_engine.set_position(self,self.static_path[0])
    def on_update(self,physic_engine:Optional[arcade.PymunkPhysicsEngine],delta_time,bullet_list):
        self.attack_cooldown-=delta_time
        if arcade.has_line_of_sight(self.position,self.player_sprite.position,self.wall_list,1000):
            if self.time_in_sight>TIME_TO_SEE:
                physic_engine.set_velocity(self,self.follow_sprite(delta_time))
                if self.attack_cooldown<=0:
                    self.attack_cooldown=1

                    bullet = BulletSprite(str(os.path.dirname(os.path.abspath(__file__)))+r"\new_assets\user_int\fireball.png",self,
                              self.player_sprite.center_x,
                                    self.player_sprite.center_y,
                                    "enemy")
                    
                    bullet_list.append(bullet)
                    physic_engine.add_sprite(bullet,
                                       mass=BULLET_MASS,
                                       damping=1,
                                       collision_type="bullet",
                                       gravity=(0,0),
                                       elasticity=0.9)
                    # Add force to bullet
                    force = (BULLET_MOVE_FORCE, 0)
                    physic_engine.apply_force(bullet, force)
            else:
                self.update_path(delta_time)
                self.time_in_sight+=delta_time
        else:
            self.time_in_sight-=delta_time
            if self.time_in_sight<0:
                self.time_in_sight = 0
            physic_engine.set_velocity(self,self.update_path(delta_time))

    def update_path(self, delta_time):
        force = [0,0]
        # Move to next point on path. Using min to avoid overshooting
        if self.cur_dir >= len(self.static_path):
            self.cur_dir = 1
        if self.center_y < self.static_path[self.cur_dir][1]:
            force[1] += min(ENEMY_SPEED, self.static_path[self.cur_dir][1] - self.center_y)
            # print(self.center_y,self.path[self.cur_dir][0],self.path[self.cur_dir][0],flush=True)
        elif self.center_y > self.static_path[self.cur_dir][1]:
            force[1] -= min(ENEMY_SPEED, self.center_y - self.static_path[self.cur_dir][1])

        if self.center_x <= self.static_path[self.cur_dir][0]:
            force[0] += min(ENEMY_SPEED, self.static_path[self.cur_dir][0] - self.center_x)
        elif self.center_x > self.static_path[self.cur_dir][0]:
            force[0] -= min(ENEMY_SPEED, self.center_x - self.static_path[self.cur_dir][0])

        force[0]*=FORCE_MULTIPLR
        force[1]*=FORCE_MULTIPLR

        """ Debug tool """
        # print(self.center_x ,self.center_y,self.static_path[self.cur_dir][0],self.static_path[self.cur_dir][1],flush=True) 
        if int(self.center_x) == int(self.static_path[self.cur_dir][0]) and int(self.center_y) == int(self.static_path[self.cur_dir][1]):
            self.cur_dir+=1

        return tuple(force)
    def follow_sprite(self,delta_time):

        force = [0,0]
        if self.center_y < self.player_sprite.center_y:
            force[1]=min(ENEMY_SPEED, self.player_sprite.center_y - self.center_y)
        elif self.center_y > self.player_sprite.center_y:
            force[1]=-min(ENEMY_SPEED, self.center_y - self.player_sprite.center_y)

        if self.center_x < self.player_sprite.center_x:
            force[0]=min(ENEMY_SPEED, self.player_sprite.center_x - self.center_x)
        elif self.center_x > self.player_sprite.center_x:
            force[0]=- min(ENEMY_SPEED, self.center_x - self.player_sprite.center_x)

        force[0]*=FORCE_MULTIPLR
        force[1]*=FORCE_MULTIPLR
        return tuple(force)

    def pymunk_moved(self, physics_engine, dx, dy, d_angle):
        # Figure out if we need to face left or right
        #Reminder fix this bs later
        if dx < -DEAD_ZONE and self.character_face_direction_x == RIGHT_FACING:
            self.character_face_direction_x = LEFT_FACING
        elif dx > DEAD_ZONE and self.character_face_direction_x == LEFT_FACING:
            self.character_face_direction_x = RIGHT_FACING

        if dy > DEAD_ZONE and self.character_face_direction_y == FRONT_FACING:
            self.character_face_direction_y = BACK_FACING
        elif dy < -DEAD_ZONE and self.character_face_direction_y == BACK_FACING:
            self.character_face_direction_y = FRONT_FACING
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
                if self.character_face_direction_x == LEFT_FACING:
                    self.texture = self.left_texture_list[self.cur_texture]
                elif self.character_face_direction_x == RIGHT_FACING:
                    self.texture = self.right_texture_list[self.cur_texture]
        elif abs(dy)>abs(dx):
            if abs(self.y_odometer) > DISTANCE_TO_CHANGE_TEXTURE:
                self.y_odometer = 0

                # Advance the walking animation
                self.cur_texture += 1
                if self.cur_texture > 1:
                    self.cur_texture = 0
                
                if self.character_face_direction_y == FRONT_FACING:
                    self.texture = self.front_texture_list[self.cur_texture]
                elif self.character_face_direction_y == BACK_FACING:
                    self.texture = self.back_texture_list[self.cur_texture]
    
class BulletSprite(arcade.Sprite):
    """ Bullet Sprite """
    def __init__(self, image, player_sprite,direction_x,direction_y,mode):
        self.player_sprite:Optional[arcade.Sprite]=player_sprite
        self.dist=0
        self.mode =mode
        #"enemy"
        #"player"
        #"impersonate"
        super().__init__(filename=image)
        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        self.position = self.player_sprite.position

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = direction_x
        dest_y = direction_y
        
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
        self.center_x += size * math.cos(angle)
        self.center_y += size * math.sin(angle)

        # Set angle of bullet
        self.angle = math.degrees(angle)

    def pymunk_moved(self, physics_engine:arcade.PymunkPhysicsEngine, dx, dy, d_angle):
        """ Handle when the sprite is moved by the physics engine. """
        # If the bullet falls below the screen, remove it
        self.dist+=abs(dx)+abs(dy) 
        if self.dist>DIST_UNTIL_DISAPPEAR:
            try:
                self.remove_from_sprite_lists()
            except:
                print("Issue to fix later",flush=True)
            return 
        
        if self.dist>DIST_UNTIL_BACKFIRE and self.mode!="gone_wrong":
            self.mode="gone_wrong"
            physics_engine.set_velocity(self,(0,0))
        if self.mode == "gone_wrong":
            x_diff = self.player_sprite.center_x - self.center_x
            y_diff = self.player_sprite.center_y - self.center_y
            angle=0
            if int(x_diff)!=0:
                angle = math.atan2(y_diff, x_diff)
            else:
                if y_diff>0:
                    angle = math.pi/2
                else:
                    angle = -math.pi/2
            physics_engine.rotate(self,angle)
            physics_engine.set_velocity(self,(0,0))
            physics_engine.apply_impulse(self,(20,0))
            
        

    