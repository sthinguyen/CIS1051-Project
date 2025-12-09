import pygame as pg
import constants as c
import random
from enemy_data import ENEMY_SPAWN_DATA

class World():
    def __init__(self, data, map_image):
        self.level = 1
        self.game_speed = 1
        self.health = c.HEALTH
        self.money = c.MONEY
        self.tile_map = []
        self.waypoints = []
        self.placeable_tiles = []
        self.level_data = data
        self.image = map_image
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0

    def process_data(self):
        for layer in self.level_data["layers"]:

            if layer["name"] == "tilemap":
                self.tile_map = layer["data"]

            elif layer["name"] == "waypoints":
                for obj in layer["objects"]:
                    base_x = obj["x"]
                    base_y = obj["y"]
                    self.process_waypoints(obj["polyline"], base_x, base_y)

            elif layer["name"] == "placeable":
                for obj in layer["objects"]:
                    tile_x = int(obj["x"] // c.TILE_SIZE)
                    tile_y = int(obj["y"] // c.TILE_SIZE)
                    self.placeable_tiles.append((tile_x, tile_y))

    def process_waypoints(self, data, base_x, base_y):
        for point in data:
            temp_x = base_x + point["x"]
            temp_y = base_y + point["y"]
            self.waypoints.append((temp_x, temp_y))

    def process_enemies(self):
        if self.level - 1 >= len(ENEMY_SPAWN_DATA):
            self.game_speed = 0
            self.enemy_list = []
            return "WIN"
        enemies = ENEMY_SPAWN_DATA[self.level - 1]
        for enemy_type in enemies:
            enemies_to_spawn = enemies[enemy_type]
            for enemy in range(enemies_to_spawn):
                self.enemy_list.append(enemy_type)
        #now randomize the list to shuffle the enemies
        random.shuffle(self.enemy_list)

    def check_level_complete(self):
        if (self.killed_enemies + self.missed_enemies) == len(self.enemy_list):
            return True

    def reset_level(self):
        self.enemy_list = []
        self.spawned_enemies = 0
        self.killed_enemies = 0
        self.missed_enemies = 0

    def draw(self, surface):
        surface.blit(self.image, (0, 0))

