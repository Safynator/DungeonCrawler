import pygame
import math
import random
import constants

class Weapon():
  def __init__(self, image, arrow_image):
    self.original_image = image
    self.angle = 0
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.arrow_image = arrow_image
    self.rect = self.image.get_rect()
    self.fired = False
    self.last_shot = pygame.time.get_ticks()

  def update(self, player, a):
    shot_cooldown = 300
    arrow = None

    self.rect.center = player.rect.center
    pos = pygame.mouse.get_pos()
    x_dist = pos[0] - self.rect.centerx
    y_dist = -(pos[1] - self.rect.centery)#-ve because pygame y coordinates increase down the screen
    self.angle = math.degrees(math.atan2(y_dist, x_dist))
    #get mouseclick
    if (pygame.mouse.get_pressed()[0] or a[pygame.K_q]) and self.fired == False and player.use == 2 and (pygame.time.get_ticks() - self.last_shot) >= shot_cooldown:
      arrow = Arrow(self.arrow_image, self.rect.centerx, self.rect.centery, self.angle)
      self.fired = True
      self.last_shot = pygame.time.get_ticks()
    #reset mouseclick
    if pygame.mouse.get_pressed()[0] == False:
      self.fired = False


    return arrow

  def draw(self, surface, player):
    if player.use == 2:
      self.image = pygame.transform.rotate(self.original_image, self.angle)
      surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))


class Arrow(pygame.sprite.Sprite):
  def __init__(self, image, x, y, angle):
    pygame.sprite.Sprite.__init__(self)
    self.original_image = image
    self.angle = angle
    self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    #calculate the horizontal and vertical speeds based on the angle
    self.dx = math.cos(math.radians(self.angle)) * constants.ARROW_SPEED
    self.dy = -(math.sin(math.radians(self.angle)) * constants.ARROW_SPEED)#-ve because pygame y coordiate increases down the screen


  def update(self, screen_scroll, obstacle_tiles, enemy_list, player, power_tile):
    #reset variables
    damage = 0
    damage_pos = None

    #reposition based on speed
    self.rect.x += screen_scroll[0] + self.dx
    self.rect.y += screen_scroll[1] + self.dy

    #check for collision between arrow and tile walls
    for obstacle in obstacle_tiles:
      if obstacle[1].colliderect(self.rect):
        self.kill()
    if power_tile != None:
      if not power_tile[5]:
        if power_tile[1].colliderect(self.rect):
          self.kill()
          player.power_level += 1
          power_tile[5] = True

    #check if arrow has gone off screen
    if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
      self.kill()

    #check collision between arrow and enemies
    for enemy in enemy_list:
      if enemy.rect.colliderect(self.rect) and enemy.alive:
        damage = 10 + (5 * (player.power_level - 1))
        damage_pos = enemy.rect
        enemy.health -= damage
        enemy.hit = True
        self.kill()
        break

    return damage, damage_pos, power_tile

  def draw(self, surface):
    surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))


class Fireball(pygame.sprite.Sprite):
  def __init__(self, image, x, y, target_x, target_y, enemy_type):
    pygame.sprite.Sprite.__init__(self)
    self.original_image = image
    x_dist = target_x - x
    y_dist = -(target_y - y)
    self.angle = math.degrees(math.atan2(y_dist, x_dist))
    self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.char = enemy_type
    #calculate the horizontal and vertical speeds based on the angle
    if self.char != 10:
      self.dx = math.cos(math.radians(self.angle)) * constants.FIREBALL_SPEED
      self.dy = -(math.sin(math.radians(self.angle)) * constants.FIREBALL_SPEED)#-ve because pygame y coordiate increases down the screen
    else:
      self.dx = math.cos(math.radians(self.angle)) * constants.ELECTRIC_LIGHTNING_SPEED
      self.dy = -(math.sin(math.radians(self.angle)) * constants.ELECTRIC_LIGHTNING_SPEED)  # -ve because pygame y coordiate increases down the screen

  def update(self, screen_scroll, player):
    #reposition based on speed
    self.rect.x += screen_scroll[0] + self.dx
    self.rect.y += screen_scroll[1] + self.dy

    #check if fireball has gone off screen
    if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
      self.kill()

    #check collision between self and player
    if player.rect.colliderect(self.rect):
      if player.hit == False:
        player.hit = True
        player.last_hit = pygame.time.get_ticks()
        player.health -= 20
      self.kill()


  def draw(self, surface):
    # pygame.draw.rect(surface, constants.RED, self.rect) # Hitbox
    surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))

class Lightning(pygame.sprite.Sprite):
  def __init__(self, image, x, y, target_x, target_y, faster=False):
    pygame.sprite.Sprite.__init__(self)
    self.original_image = image
    x_dist = target_x - x
    y_dist = -(target_y - y)
    self.angle = math.degrees(math.atan2(y_dist, x_dist))
    self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.faster = faster
    #calculate the horizontal and vertical speeds based on the angle
    if not self.faster:
      self.dx = math.cos(math.radians(self.angle)) * constants.MINI_LIGHTNING_SPEED
      self.dy = -(math.sin(math.radians(self.angle)) * constants.MINI_LIGHTNING_SPEED)#-ve because pygame y coordiate increases down the screen
    else:
      self.dx = math.cos(math.radians(self.angle)) * constants.ELECTRIC_LIGHTNING_SPEED
      self.dy = -(math.sin(math.radians(self.angle)) * constants.ELECTRIC_LIGHTNING_SPEED)  # -ve because pygame y coordiate increases down the screen

  def update(self, screen_scroll, player):
    #reposition based on speed
    self.rect.x += screen_scroll[0] + self.dx
    self.rect.y += screen_scroll[1] + self.dy

    #check if fireball has gone off screen
    if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
      self.kill()

    #check collision between self and player
    if player.rect.colliderect(self.rect):
      if player.hit == False:
        player.hit = True
        player.last_hit = pygame.time.get_ticks()
        player.health -= 20
      self.kill()


  def draw(self, surface):
    # pygame.draw.rect(surface, constants.RED, self.rect) # Hitbox
    surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), self.rect.centery - int(self.image.get_height()/2)))


class Sword:
  def __init__(self, player, image_s, image_f):
    self.power = 10 + player.power_level * 2
    self.original_image = image_s
    self.image = image_s
    self.range = constants.SWORD_RANGE
    self.flipped_image = image_f
    self.angle = 0
    self.cooldown = 0
    self.rect = self.image.get_rect()
    self.hitbox = self.image.get_rect()
    self.swing_time = 0
    self.stun = 0

  def update(self, player, enemy_list, power_tile, a, fireballs):
    self.power = (player.power_level * 5) + 10
    self.swing_time -= 1
    self.cooldown -= 1
    self.stun -= 1
    self.rect.center = player.rect.center
    if self.swing_time <= 0:
      self.hitbox.center = player.rect.center
    damage = 0
    enemies_hit = 0
    damage_pos = None
    pos = pygame.mouse.get_pos()
    x_dist = pos[0] - self.rect.centerx
    y_dist = -(pos[1] - self.rect.centery) #-ve because pygame y coordinates increase down the screen
    self.angle = math.degrees(math.atan2(y_dist, x_dist))
    self.dx = 0
    self.dy = 0

    if (pygame.mouse.get_pressed()[0] or a[pygame.K_q]) and player.use == 1 and self.cooldown <= 0:
      self.cooldown = 30
      self.dx = math.cos(math.radians(self.angle)) * constants.SWORD_RANGE
      self.dy = -(math.sin(math.radians(self.angle)) * constants.SWORD_RANGE)
      self.hitbox.x += self.dx
      self.hitbox.y += self.dy
      self.swing_time = constants.SWORD_SWING_TIME
      self.cooldown *= 1 - (player.score / 100)
      self.swing_time*= 1 - (player.score / 100)

      if power_tile != None:
        if not power_tile[5]:
          if power_tile[1].colliderect(self.rect):
              player.power_level += 1
              power_tile[5] = True


      for enemy in enemy_list:
        if enemy.rect.colliderect(self.hitbox) and enemy.alive and enemies_hit < 2:
          damage_pos = enemy.rect
          enemy.health -= self.power
          enemy.hit = True
          damage = self.power
          enemies_hit += 1

    for fireball in fireballs:
      if self.hitbox.colliderect(fireball.rect) and self.swing_time > 0 and self.stun <= 0:
        fireball.kill()
        self.cooldown = 45
        self.swing_time = 45
        self.stun = 45
        self.cooldown *= 1 - (player.score / 100)
        self.swing_time *= 1 - (player.score / 100)
        self.stun *= 1 - (player.score / 100)

    return damage, damage_pos, power_tile, enemy_list, fireballs

  
  def draw(self, surface, player):
    check = 0
    if player.use == 1:
      dist = 30
      pos = pygame.mouse.get_pos()

      if pos[1] > player.rect.top and pos[1] < player.rect.bottom:
        check = 1
        if pos[0] > player.rect.centerx:
          self.rect.centerx += dist
        else:
          self.rect.centerx -= dist
      else:
        if pos[0] > player.rect.centerx:
          self.rect.centerx += dist
        else:
          self.rect.centerx -= dist
      if pos[0] > player.rect.left and pos[0] < player.rect.right:
        self.rect.centerx = player.rect.centerx
        if pos[1] > player.rect.centery:
          self.rect.centery += dist
        if pos[1] < player.rect.centery:
          self.rect.centery -= dist
      else:
        if pos[1] > player.rect.centery:
          self.rect.centery += dist
        if pos[1] < player.rect.centery:
          self.rect.centery -= dist
      if check == 1:
        self.rect.centery = player.rect.centery
      if self.angle > 180:
        self.image = pygame.transform.rotate(self.flipped_image, self.angle - 180)
      else:
        self.image = pygame.transform.rotate(self.original_image, self.angle)
      if self.swing_time > 0:
        # pygame.draw.rect(surface, constants.BLUE, self.hitbox) # Hitbox
        surface.blit(self.image, (self.hitbox.centerx - int(self.image.get_width() // 2), self.hitbox.centery - int(self.image.get_height() / 2)))
      else:
        # pygame.draw.rect(surface, constants.BLUE, self.hitbox) # Hitbox
        surface.blit(self.image, (self.rect.centerx - int(self.image.get_width()//2), self.rect.centery - int(self.image.get_height()/2)))

