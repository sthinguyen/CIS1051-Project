import pygame as pg
from pygame.math import Vector2
import math
import constants as c
from enemy_data import ENEMY_DATA

class Enemy(pg.sprite.Sprite):
  def __init__(self, enemy_type, waypoints, images):
    pg.sprite.Sprite.__init__(self)
    self.enemy_type = enemy_type
    self.waypoints = waypoints
    self.pos = Vector2(self.waypoints[0])
    self.target_waypoint = 1
    self.health = ENEMY_DATA.get(enemy_type)["health"]
    self.speed = ENEMY_DATA.get(enemy_type)["speed"]
    self.hit_timer = 0
    self.angle = 0
    self.original_image = images.get(enemy_type)
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos
    #bobbing effect
    self.bob_offset = 0
    self.bob_speed = 0.1
    self.bob_height = 3
    self.bob_angle = 0

  def update(self, world):
    #bobbing effect pt 2
    self.bob_angle += self.bob_speed * world.game_speed
    self.bob_offset = math.sin(self.bob_angle) * self.bob_height
    
    self.move(world)
    self.rotate()
    self.check_alive(world)
    if self.hit_timer > 0:
      self.hit_timer -= 1

  def draw(self, screen):
    draw_pos = self.pos + pg.Vector2(0, self.bob_offset)
    if self.hit_timer > 0:
      red_effect = self.original_image.copy()
      red_effect.fill((255, 0, 0), special_flags=pg.BLEND_MULT)
      rotated_image = pg.transform.rotate(red_effect, self.angle)
      rect = rotated_image.get_rect(center=draw_pos)
      screen.blit(rotated_image, rect)
    else:
      rotated_image = pg.transform.rotate(self.original_image, self.angle)
      rect = rotated_image.get_rect(center=draw_pos)
      screen.blit(rotated_image, rect)

  def move(self, world):
    #define a target waypoint
    if self.target_waypoint < len(self.waypoints):
      self.target = Vector2(self.waypoints[self.target_waypoint])
      self.movement = self.target - self.pos
    else:
      #enemy has reached the end of the path
      self.kill()
      enemy_damage = ENEMY_DATA[self.enemy_type]["damage"]
      world.health -= enemy_damage
      world.missed_enemies += 1

    #calculate distance to target
    dist = self.movement.length()
    #check if remaining distance is greater than the enemy speed
    if dist >= (self.speed * world.game_speed):
      self.pos += self.movement.normalize() * (self.speed * world.game_speed)
    else:
      if dist != 0:
        self.pos += self.movement.normalize() * dist
      self.target_waypoint += 1

  def rotate(self):
    #calculate distance to next waypoint
    dist = self.target - self.pos
    #use distance to calculate angle
    self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
    #rotate image and update rectangle
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()

  def check_alive(self, world):
    if self.health <= 0:
      world.killed_enemies += 1
      world.money += c.KILL_REWARD
      if self.enemy_type == "boss":
        world.money += c.BOSS_KILL_BONUS
      self.kill()
