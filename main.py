import pygame
from pygame import mixer
import csv
import constants
from character import Character
from weapon import Weapon
from weapon import Sword
from items import Item
from world import World
from button import Button
import datetime
import puzzles
from puzzles import moving_Blocks

mixer.init()
pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

#create clock for maintaining frame rate
clock = pygame.time.Clock()

#define game variables
level = 1
start_game = False
pause_game = False
start_intro = False
screen_scroll = [0, 0]

#define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False
slow = False

print("Game made by Safy Rahman")

#define font
font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

#helper function to scale image
def scale_img(image, scale):
  w = image.get_width()
  h = image.get_height()
  return pygame.transform.scale(image, (w * scale, h * scale))

#load music and sounds
pygame.mixer.music.load("assets/audio/music.wav")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
shot_fx = pygame.mixer.Sound("assets/audio/arrow_shot.mp3")
shot_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound("assets/audio/arrow_hit.wav")
hit_fx.set_volume(0.5)
coin_fx = pygame.mixer.Sound("assets/audio/coin.wav")
coin_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound("assets/audio/heal.wav")
heal_fx.set_volume(0.5)

#load button images
start_img = scale_img(pygame.image.load("assets/images/buttons/button_start.png").convert_alpha(), constants.BUTTON_SCALE)
exit_img = scale_img(pygame.image.load("assets/images/buttons/button_exit.png").convert_alpha(), constants.BUTTON_SCALE)
restart_img = scale_img(pygame.image.load("assets/images/buttons/button_restart.png").convert_alpha(), constants.BUTTON_SCALE)
resume_img = scale_img(pygame.image.load("assets/images/buttons/button_resume.png").convert_alpha(), constants.BUTTON_SCALE)

#load heart images
heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

#load coin images
coin_images = []
for x in range(4):
  img = scale_img(pygame.image.load(f"assets/images/items/coin_f{x}.png").convert_alpha(), constants.ITEM_SCALE)
  coin_images.append(img)

#load potion image
red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(red_potion)

#load weapon images
bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)
fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)
lightning_image = scale_img(pygame.image.load("assets/images/weapons/lightning.png").convert_alpha(), constants.LIGHTNING_SCALE)
flame_fireball_image = scale_img(pygame.image.load("assets/images/weapons/fireball.png").convert_alpha(), constants.FLAME_FIREBALL_SCALE)
sword_image = scale_img(pygame.image.load("assets/images/weapons/sword.png").convert_alpha(), constants.SWORD_SCALE)
flipped_sword_image = scale_img(pygame.image.load("assets/images/weapons/sword2.png").convert_alpha(), constants.SWORD_SCALE)


#load tilemap images
tile_list = []
for x in range(constants.TILE_TYPES):
  tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
  tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
  tile_list.append(tile_image)

final_boss = None

#load character images
mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_fire_demon", "dark_flame", "big_electric_demon", "dark_electric", "dark_electric_fire"]

animation_types = ["idle", "run"]
for mob in mob_types:
  #load images
  animation_list = []
  for animation in animation_types:
    #reset temporary list of images
    temp_list = []
    for i in range(4):
      img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
      if mob == "dark_flame" or mob == "dark_electric_fire":
        img = scale_img(img, .30)
      elif mob == "dark_electric":
        img = scale_img(img, .75)
      else:
        img = scale_img(img, constants.SCALE)
      temp_list.append(img)
    animation_list.append(temp_list)
  mob_animations.append(animation_list)


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#function for displaying game info
def draw_info():
  pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 60)) # Heights were 50
  pygame.draw.line(screen, constants.WHITE, (0, 60), (constants.SCREEN_WIDTH, 60))
  #draw lives
  half_heart_drawn = False
  for i in range(5):
    if player.health >= ((i + 1) * 20):
      screen.blit(heart_full, (10 + i * 60, 0)) # Was multiplied by 50
    elif (player.health % 20 > 0) and half_heart_drawn == False:
      screen.blit(heart_half, (10 + i * 60, 0)) # Was multiplied by 50
      half_heart_drawn = True
    else:
      screen.blit(heart_empty, (10 + i * 60, 0)) # Was multiplied by 50

  #level
  draw_text("LEVEL: " + str(level), font, constants.WHITE, constants.SCREEN_WIDTH / 2, 25) # 15
  #show score
  draw_text(f"X{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 25) # 15

#function to reset level
def reset_level():
  damage_text_group.empty()
  arrow_group.empty()
  item_group.empty()
  fireball_group.empty()
  lightning_group.empty()

  #create empty tile list
  data = []
  for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    data.append(r)

  return data



#damage text class
class DamageText(pygame.sprite.Sprite):
  def __init__(self, x, y, damage, color):
    pygame.sprite.Sprite.__init__(self)
    self.image = font.render(damage, True, color)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    #reposition based on screen scroll
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]

    #move damage text up
    self.rect.y -= 1
    #delete the counter after a few seconds
    self.counter += 1
    if self.counter > 30:
      self.kill()

#class for handling screen fade
class ScreenFade():
  def __init__(self, direction, colour, speed):
    self.direction = direction
    self.colour = colour
    self.speed = speed
    self.fade_counter = 0

  def fade(self):
    fade_complete = False
    self.fade_counter += self.speed
    if self.direction == 1:#whole screen fade
      pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, constants.SCREEN_WIDTH // 2, constants.SCREEN_HEIGHT))
      pygame.draw.rect(screen, self.colour, (constants.SCREEN_WIDTH // 2 + self.fade_counter, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
      pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT // 2))
      pygame.draw.rect(screen, self.colour, (0, constants.SCREEN_HEIGHT // 2 + self.fade_counter, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
      if self.fade_counter >= constants.SCREEN_WIDTH:
        fade_complete = True
    elif self.direction == 2:#vertical screen fade down
      pygame.draw.rect(screen, self.colour, (0, 0, constants.SCREEN_WIDTH, 0 + self.fade_counter))
      if self.fade_counter >= constants.SCREEN_HEIGHT:
        fade_complete = True



    return fade_complete


#create empty tile list
world_data = []
for row in range(constants.ROWS):
  r = [-1] * constants.COLS
  world_data.append(r)
#load in level data and create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
  reader = csv.reader(csvfile, delimiter = ",")
  for x, row in enumerate(reader):
    for y, tile in enumerate(row):
      world_data[x][y] = int(tile)


world = World()
power_tile, boss, boss2, final_boss = world.process_data(world_data, tile_list, item_images, mob_animations, level)

#create player
player = world.player
#create player's weapon
bow = Weapon(bow_image, arrow_image)
sword = Sword(player, sword_image, flipped_sword_image)

#extract enemies from world data
enemy_list = world.character_list

#create sprite groups
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()
lightning_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 33, 0, coin_images, True) # 23
item_group.add(score_coin)
#add the items from the level data
for item in world.item_list:
  item_group.add(item)


#create screen fades
intro_fade = ScreenFade(1, constants.BLACK, 4)
death_fade = ScreenFade(2, constants.PINK, 4)

#create button
start_button = Button(constants.SCREEN_WIDTH // 2 - 145, constants.SCREEN_HEIGHT // 2 - 150, start_img)
exit_button = Button(constants.SCREEN_WIDTH // 2 - 110, constants.SCREEN_HEIGHT // 2 + 50, exit_img)
restart_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 50, restart_img)
resume_button = Button(constants.SCREEN_WIDTH // 2 - 175, constants.SCREEN_HEIGHT // 2 - 150, resume_img)



draw_text2 = font.render("Made by Safy Rahman", True, constants.WHITE)

player_tile = None

#main game loop
run = True
q = 0
p = 0
o = 0
z = 0
a = 0
l8 = 0
l11 = 0
l9 = 0
l10 = 0
l14 = 0
end = 0
moving_block = None
level_complete = False

boss_health_timer = 0

printed = False
while run:

  if level == constants.LAST_LEVEL:
    end += 1
    end_time = datetime.datetime.now()
    print(" GG ")
    print("Thank you for playing! ")
    print("Final Time: ", end_time - start_time)
    run = False


  if level == 3 and p == 0:
    p += 1
    player.spawn_time = 90
  if level == 5:
    if a <= 10 and player.rect.centerx < 2000:
      a += 1
      player.spawn_time = 90
      boss.rect.center = player.rect.center

  #control frame rate
  clock.tick(constants.FPS)
  damage = None
  if q == 60:
    run = False

  if start_game == False:
    screen.fill(constants.MENU_BG)
    screen.blit(draw_text2, ((constants.SCREEN_WIDTH // 2 - draw_text2.get_width() / 2) + 50,
                             (constants.SCREEN_HEIGHT / 2 - draw_text2.get_height() / 2) + 200))

    if start_button.draw(screen):
      start_game = True
      start_intro = True
      start_time = datetime.datetime.now()
    if exit_button.draw(screen):
      run = False
  else:
    # a += 1
    # if a >= 60 and level == 5:
    #   a = 0
    #   print(boss.rect.center)
    #   print(player.rect.center)

    if pause_game == True:
      screen.fill(constants.MENU_BG)
      if resume_button.draw(screen):
        pause_game = False
      if exit_button.draw(screen):
        run = False
    else:
      screen.fill(constants.BG)

      if player.alive:
        #calculate player movement
        dx = 0
        dy = 0
        if moving_right == True:
          dx = constants.SPEED
        if moving_left == True:
          dx = -constants.SPEED
        if moving_up == True:
          dy = -constants.SPEED
        if moving_down == True:
          dy = constants.SPEED
        if slow:
          dx * .5
          dy * .5
          print("Slower")

        if level == 6: # Puzzles
          world.map_tiles, player_tile, level_complete = puzzles.breaking_tiles(player, world.map_tiles, tile_list[21], player_tile)
        if level == 7:
          if not o:
            o += 1
            l8 = 0
            moving_block = puzzles.moving_Blocks(tile_list[24], world.block_tile_start[1].centerx, world.block_tile_start[1].centery)

          world.map_tiles, player_tile = puzzles.breaking_tiles_door(player, world.map_tiles, world.door, tile_list[21],
                                                                                player_tile, 4)
          level_complete = moving_block.update(player, sword, world.obstacle_tiles, world.block_tile, screen_scroll, world.moving_obstacles, world.door)
        if level == 8:
          for tile in world.map_tiles:
            if tile[4] == 29:
              if tile[1].collidepoint(player.rect.center):
                player.alive = False
          if not l8:
            l8 += 1
            moving_block = puzzles.moving_Blocks(tile_list[24], world.block_tile_start[1].centerx, world.block_tile_start[1].centery)
          level_complete = moving_block.update(player, sword, world.obstacle_tiles, world.block_tile, screen_scroll, world.moving_obstacles, world.door)
        if level == 11:
          if not l11:
            l11 += 1
            moving_block = puzzles.moving_Blocks(tile_list[24], world.block_tile_start[1].centerx, world.block_tile_start[1].centery)
            moving_block.rect.center = player.rect.center

          world.map_tiles, player_tile = puzzles.breaking_tiles_door(player, world.map_tiles, world.door, tile_list[21],
                                                                     player_tile)
          level_complete = moving_block.update(player, sword, world.obstacle_tiles, world.block_tile, screen_scroll, world.moving_obstacles, world.door)


          # print("Block", moving_block.rect.centerx, moving_block.rect.centery)
          # print("Player", player.rect.centerx, player.rect.centery)

        if level_complete == True:
          start_intro = True
          level += 1
          world_data = reset_level()
          # load in level data and create world
          with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = World()
          power_tile, boss, boss2, final_boss = world.process_data(world_data, tile_list, item_images, mob_animations, level)
          temp_hp = player.health
          temp_score = player.score
          temp_power = player.power_level
          player = world.player
          player.health = temp_hp
          player.power_level = temp_power
          player.score = temp_score
          enemy_list = world.character_list
          score_coin = Item(constants.SCREEN_WIDTH - 115, 33, 0, coin_images, True)  # y: 23
          item_group.add(score_coin)
          # add the items from the level data
          for item in world.item_list:
            item_group.add(item)
        if level_complete:
          level_complete = False

        #move player
        screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)

        #update all objects
        world.update(screen_scroll, power_tile)
        for enemy in enemy_list:
          fireball, lightning = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image, flame_fireball_image, lightning_image)
          if fireball:
            fireball_group.add(fireball)
          if lightning:
            lightning_group.add(lightning)
          if enemy.alive:
            enemy.update()
        player.update()
        if player.use == 1:
          damage, damage_pos, power_tile, enemy_list, fireball_group = sword.update(player, enemy_list, power_tile, pygame.key.get_pressed(), fireball_group)
        else:
          arrow = bow.update(player, pygame.key.get_pressed())
          if arrow:
            arrow_group.add(arrow)
            shot_fx.play()
        for arrow in arrow_group:
          damage, damage_pos, power_tile = arrow.update(screen_scroll, world.obstacle_tiles, enemy_list, player, power_tile)
        if damage:
          damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
          damage_text_group.add(damage_text)
          hit_fx.play()
          damage, damage_pos = None, None


        damage_text_group.update()
        fireball_group.update(screen_scroll, player)
        lightning_group.update(screen_scroll, player)
        item_group.update(screen_scroll, player, coin_fx, heal_fx)

      #draw player on screen
      world.draw(screen)
      item_group.draw(screen)
      for enemy in enemy_list:
        enemy.draw(screen)
        if enemy.char_type == 10:
          if boss_health_timer == 1:
            damage_text = DamageText(enemy.rect.centerx, enemy.rect.top, str(enemy.health), constants.BLACK)
            damage_text_group.add(damage_text)
          elif boss_health_timer == 60:
            boss_health_timer = 0
          boss_health_timer += 1
      player.draw(screen)
      bow.draw(screen, player)
      for arrow in arrow_group:
        arrow.draw(screen)
      for fireball in fireball_group:
        fireball.draw(screen)
      for lightning in lightning_group:
        lightning.draw(screen)
      damage_text_group.draw(screen)
      if moving_block != None:
        if level == 7 or level == 8 or level == 11:
          moving_block.draw(screen)
      draw_info()
      score_coin.draw(screen)
      sword.draw(screen, player)

      if level == 3 or level == 5:
        if not boss.alive:
          start_intro = True
          level += 1
          world_data = reset_level()
          # load in level data and create world
          with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = World()
          power_tile, boss, boss2, final_boss = world.process_data(world_data, tile_list, item_images, mob_animations, level)
          temp_hp = player.health
          temp_score = player.score
          temp_power = player.power_level
          player = world.player
          player.health = temp_hp
          player.power_level = temp_power
          player.score = temp_score
          enemy_list = world.character_list
          score_coin = Item(constants.SCREEN_WIDTH - 115, 33, 0, coin_images, True)  # 23
          item_group.add(score_coin)
          # add the items from the level data
          for item in world.item_list:
            item_group.add(item)

      #check level complete
      if level == 9 or level == 10:
        if not l9:
          boss2.rect.center = player.rect.center
          l9 += 1
        if not l10:
          boss2.rect.center = player.rect.center
          l10 += 1
        if not boss2.alive:
          start_intro = True
          level += 1
          world_data = reset_level()
          # load in level data and create world
          with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = World()
          power_tile, boss, boss2, final_boss = world.process_data(world_data, tile_list, item_images, mob_animations, level)
          temp_hp = player.health
          temp_score = player.score
          temp_power = player.power_level
          player = world.player
          player.health = temp_hp
          player.power_level = temp_power
          player.score = temp_score
          enemy_list = world.character_list
          score_coin = Item(constants.SCREEN_WIDTH - 115, 33, 0, coin_images, True) # 23
          item_group.add(score_coin)
          # add the items from the level data
          for item in world.item_list:
            item_group.add(item)

      

      if level == 4 or level == 12:
        left = True
        for enemy in enemy_list:
          if enemy.alive:
            left = False
        if left == True:
          start_intro = True
          level += 1
          world_data = reset_level()
          # load in level data and create world
          with open(f"levels/level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
              for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
          world = World()
          power_tile, boss, boss2, final_boss = world.process_data(world_data, tile_list, item_images, mob_animations, level)
          temp_hp = player.health
          temp_score = player.score
          temp_power = player.power_level
          player = world.player
          player.health = temp_hp
          player.power_level = temp_power
          player.score = temp_score
          enemy_list = world.character_list
          score_coin = Item(constants.SCREEN_WIDTH - 115, 33, 0, coin_images, True) # 23
          item_group.add(score_coin)
          # add the items from the level data
          for item in world.item_list:
            item_group.add(item)
          level_complete = False
              
      if level == 13 or level == 14:
        if not boss.alive and not boss2.alive:
          level_complete = True

      if level == 15:
        if not final_boss.alive:
          level_complete = True

      if level_complete == True:
        start_intro = True
        level += 1
        world_data = reset_level()
        #load in level data and create world
        with open(f"levels/level{level}_data.csv", newline="") as csvfile:
          reader = csv.reader(csvfile, delimiter = ",")
          for x, row in enumerate(reader):
            for y, tile in enumerate(row):
              world_data[x][y] = int(tile)
        world = World()
        power_tile, boss, boss2, final_boss = world.process_data(world_data, tile_list, item_images, mob_animations, level)
        temp_hp = player.health
        temp_score = player.score
        temp_power = player.power_level
        player = world.player
        player.health = temp_hp
        player.power_level = temp_power
        player.score = temp_score
        enemy_list = world.character_list
        score_coin = Item(constants.SCREEN_WIDTH - 115, 33, 0, coin_images, True) # y: 23
        item_group.add(score_coin)
        #add the items from the level data
        for item in world.item_list:
          item_group.add(item)


      if level_complete:
        level_complete = False


      #show intro
      if start_intro == True:
        if intro_fade.fade():
          start_intro = False
          intro_fade.fade_counter = 0


      #show death screen
      if player.alive == False:
        if death_fade.fade():
          if restart_button.draw(screen):
            death_fade.fade_counter = 0
            q = 0
            p = 0
            o = 0
            z = 0
            a = 0
            l8 = 0
            l9 = 0
            l11 = 0
            start_intro = True
            world_data = reset_level()
            #load in level data and create world
            with open(f"levels/level{level}_data.csv", newline="") as csvfile:
              reader = csv.reader(csvfile, delimiter = ",")
              for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                  world_data[x][y] = int(tile)
            world = World()
            temp_power_tile = power_tile
            power_tile, boss, boss2, final_boss = world.process_data(world_data, tile_list, item_images, mob_animations, level)
            if power_tile != None:
              power_tile[5] = temp_power_tile[5]
            temp_score = player.score
            temp_power = player.power_level
            player = world.player
            player.power_level = temp_power
            player.score = temp_score
            enemy_list = world.character_list
            score_coin = Item(constants.SCREEN_WIDTH - 115, 33, 0, coin_images, True) # 23
            item_group.add(score_coin)

            #add the items from the level data
            for item in world.item_list:
              item_group.add(item)

            start_time = datetime.datetime.now()

  #event handler
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    #take keyboard presses
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_a:
        moving_left = True
      if event.key == pygame.K_d:
        moving_right = True
      if event.key == pygame.K_w:
        moving_up = True
      if event.key == pygame.K_s:
        moving_down = True
      if event.key == pygame.K_ESCAPE:
        pause_game = True
      if event.key == pygame.K_1:
        player.use = 1
      if event.key == pygame.K_2:
        player.use = 2
      if event.key == pygame.K_LSHIFT:
        slow = True
      else:
        slow = False


    #keyboard button released
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_w:
        moving_up = False
      if event.key == pygame.K_s:
        moving_down = False


  pygame.display.update()


pygame.quit()