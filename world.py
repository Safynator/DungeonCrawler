from character import Character
from items import Item
import constants

class World():
  def __init__(self):
    self.map_tiles = []
    self.obstacle_tiles = []
    self.exit_tile = None
    self.item_list = []
    self.player = None
    self.character_list = []
    self.broken_tiles = []


  def process_data(self, data, tile_list, item_images, mob_animations, level = 1):
    self.level_length = len(data)
    self.tile_images = tile_list
    power_tile = None
    boss = None
    boss2 = None
    ultimate_enemy = None
    self.door = None
    self.block_tile = None
    self.block_tile_start = None
    self.moving_obstacles = []
    #iterate through each value in level data file

    q = 0
    a = 0
    for y, row in enumerate(data):
      for x, tile in enumerate(row):
        image = tile_list[tile]
        image_rect = image.get_rect()
        image_x = x * constants.TILE_SIZE
        image_y = y * constants.TILE_SIZE
        image_rect.center = (image_x, image_y)
        tile_data = [image, image_rect, image_x, image_y, tile, False]
        if tile == 7:
          self.obstacle_tiles.append(tile_data)
        elif tile == 8:
          self.exit_tile = tile_data
        elif tile == 9:
          coin = Item(image_x, image_y, 0, item_images[0])
          self.item_list.append(coin)
          tile_data[0] = tile_list[0]
        elif tile == 10:
          potion = Item(image_x, image_y, 1, [item_images[1]])
          self.item_list.append(potion)
          tile_data[0] = tile_list[0]
        elif tile == 11:
          player = Character(image_x, image_y, 100, mob_animations, 0, False, 1, level)
          self.player = player
          player.power_level = 1
          tile_data[0] = tile_list[0]
        elif tile >= 12 and tile <= 16:
          enemy = Character(image_x, image_y, 50+(50*constants.DIFFICULTY), mob_animations, tile - 11, False, 1, level)
          self.character_list.append(enemy)
          tile_data[0] = tile_list[0]
        elif tile == 17:
          enemy = Character(image_x, image_y, 250+(50*constants.DIFFICULTY), mob_animations, 6, True, 2, level)
          if not q:
            boss = enemy
          if level == 3:
            boss = enemy
          self.character_list.append(enemy)
          tile_data[0] = tile_list[0]
        elif tile == 19:
          enemy = Character(image_x, image_y, 500+(50*constants.DIFFICULTY), mob_animations, 7, True, 2, level)
          if not ultimate_enemy:
            boss = enemy
            q = 1
          self.character_list.append(enemy)
          tile_data[0] = tile_list[0]
        elif tile == 18:
          power_tile = tile_data
        elif tile == 20:
          self.player_tile = tile_data
        elif tile == 22:
          tile_data.append(None) # Direction
          self.door = tile_data
        elif tile == 23:
          self.block_tile = tile_data
        elif tile == 24:
          self.block_tile_start = tile_data
          tile_data[0] = self.tile_images[0]
        elif tile == 25:
          self.moving_obstacles.append(tile_data)
        elif tile == 26:
          enemy = Character(image_x, image_y, 200+(50*constants.DIFFICULTY), mob_animations, 8, True, 2, level)
          if not a:
            boss2 = enemy
            a += 1
          self.character_list.append(enemy)
        elif tile == 27:
          enemy = Character(image_x, image_y, 400+(50*constants.DIFFICULTY), mob_animations, 9, True, 2, level)
          if not ultimate_enemy:
            boss2 = enemy
            a = 1
            self.character_list.append(enemy)
          tile_data[0] = tile_list[0]
        elif tile == 28:
          enemy = Character(image_x, image_y, 600+(75*constants.DIFFICULTY), mob_animations, 10, True, 2, level)
          boss = None
          boss2 = None
          ultimate_enemy = enemy
          a = 1
          q = 1
          self.character_list.append(enemy)
          tile_data[0] = tile_list[0]

        #add image data to main tiles list
        if tile >= 0:
          self.map_tiles.append(tile_data)
    return power_tile, boss, boss2, ultimate_enemy

  def update(self, screen_scroll, power_tile):
    for tile in self.map_tiles:
      tile[2] += screen_scroll[0]
      tile[3] += screen_scroll[1]
      tile[1].center = (tile[2], tile[3])
      if tile == power_tile and power_tile[5]:
        tile[0] = self.tile_images[0]
      if tile == self.door and self.door[5]:
        tile[0] = self.tile_images[0]


  def draw(self, surface):
    for tile in self.map_tiles:
      surface.blit(tile[0], tile[1])