import pygame
import constants
import math

def breaking_tiles_door(player, world_tiles, door, broken_tile_image, player_tile, direction = None):
    puzzle_complete = False

    if door:
        puzzle_complete = True
        a = 0
        for tile in world_tiles:
            if player_tile != None and player_tile == tile:
                if not tile[1].collidepoint(player.rect.centerx, player.rect.centery):
                    tile[5] = True
                    tile[0] = broken_tile_image
                    player_tile = None
        for tile in world_tiles:
            if tile[4] == 20:
                if tile[1].collidepoint(player.rect.centerx, player.rect.centery):
                    if not tile[5]:
                        player_tile = tile
                    else:
                        player.alive = False
                if not tile[5]:
                    a += 1
                    if a == 2:
                        puzzle_complete = False
        if puzzle_complete:
            door[5] = True
        if player.rect.colliderect(door[1]) and not puzzle_complete:
            if direction == 1: # 1 is up
                player.rect.top = door[1].bottom
            if direction == 2: # 2 is down
                player.rect.bottom = door[1].top
            if direction == 3: # 3 is left
                player.rect.left = door[1].right
            if direction == 4:
                player.rect.right = door[1].left
    return world_tiles, player_tile


def breaking_tiles(player, world_tiles, broken_tile_image, player_tile):
    puzzle_complete = True
    a = 0
    for tile in world_tiles:
        if player_tile != None and player_tile == tile:
            if not tile[1].collidepoint(player.rect.centerx, player.rect.centery):
                tile[5] = True
                tile[0] = broken_tile_image
                player_tile = None
    for tile in world_tiles:
        if tile[4] == 20:
            if tile[1].collidepoint(player.rect.centerx, player.rect.centery):
                if not tile[5]:
                    player_tile = tile
                else:
                    player.alive = False
            if not tile[5]:
                a += 1
                if a == 2:
                    puzzle_complete = False
    return world_tiles, player_tile, puzzle_complete

# def moving_block_puzzle(player, sword, world_tiles, walls, block_tile, tile_pictures):
#     puzzle_complete = False
#     dir = None
#     if sword.hitbox.colliderect(block_tile[1]):
#         if (block_tile[1].bottom > player.rect.centery and block_tile[1].top < player.rect.centery):
#             if block_tile[1].right <= player.rect.left:
#                 dir = 1 # Left
#             else:
#                 dir = 2 # Right
#         elif block_tile[1].left < player.rect.centerx and block_tile[1].right > player.rect.centerx:
#             if block_tile[1].top <= player.rect.centery:
#                 dir = 3 # Down
#             if block_tile[1].bottom >= player.rect.centery:
#                 dir = 4 # Up
#         if dir != None:
#             check = 0
#             for y, row in enumerate(world_tiles):
#                 for x, tile in enumerate(row):
#                     if tile == block_tile:
#                         tile[0] = tile_pictures[tile[4]]
#                         if dir == 1:
#                             for i in range(1, 6):
#                                 for wall in walls:
#                                     if tile[y][x - i] != wall:
#                                         block_tile = tile
#                                         world_tiles[y][x - i][0] = tile_pictures[23]
#                                     else:
#                                         check = 1
#                                 if check != 0:
#                                     break
#                         if dir == 2:
#                             for i in range(1, 6):
#                                 for wall in walls:
#                                     if tile[y][x + i] != wall:
#                                         block_tile = tile
#                                         world_tiles[y][x + i][0] = tile_pictures[23]
#                                     else:
#                                         check = 1
#                                 if check != 0:
#                                     break
#                         if dir == 3:
#                             for i in range(1, 6):
#                                 for wall in walls:
#                                     if tile[y + i][x] != wall:
#                                         block_tile = tile
#                                         world_tiles[y + i][x][0] = tile_pictures[23]
#                                     else:
#                                         check = 1
#                                 if check != 0:
#                                     break
#                         if dir == 4:
#                             for i in range(1, 6):
#                                 for wall in walls:
#                                     if tile[y - i][x] != wall:
#                                         block_tile = tile
#                                         world_tiles[y - i][x][0] = tile_pictures[23]
#                                     else:
#                                         check = 1
#                                 if check != 0:
#                                     break
#     for tile in world_tiles:
#         if tile[4] == 24:
#             if block_tile == tile:
#                 puzzle_complete = True
#
#     return world_tiles, block_tile, puzzle_complete

class moving_Blocks:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dir = None
        self.speed = 5
        self.complete = False
        self.spacer = 0
        # self.rect.center = (1067, 371)

    def update(self, player, sword, walls, pressure_tile, screen_scroll, obstacles, door):
        a = 0
        self.rect.centerx += screen_scroll[0]
        self.rect.centery += screen_scroll[1]
        stoppers = [walls, obstacles]
        if door != None:
            if not door[5]:
                stoppers.append([door])
        if not self.complete:
            if sword.swing_time >= 1:
                if sword.rect.colliderect(self.rect):
                    if self.dir == None:
                        if (self.rect.bottom > player.rect.centery and self.rect.top < player.rect.centery):
                            a += 1
                            if self.rect.right <= player.rect.left:
                                self.dir = 1  # Left
                            else:
                                self.dir = 2  # Right
                        if self.rect.left < player.rect.centerx and self.rect.right > player.rect.centerx:
                            a += 1
                            if self.rect.top >= player.rect.centery:
                                self.dir = 3  # Down
                            else:
                                self.dir = 4  # Up
                        if a == 2 or a == 0:
                            pos = pygame.mouse.get_pos()
                            x_dist = pos[0] - self.rect.centerx
                            y_dist = -(pos[1] - self.rect.centery)  # -ve because pygame y coordinates increase down the screen
                            self.angle = math.degrees(math.atan2(y_dist, x_dist))
                            if self.angle < 45 or self.angle > 315:
                                self.dir = 2
                            if self.angle < 225 and self.angle > 135:
                                self.dir = 1
                            if self.angle < 135 and self.angle > 45:
                                self.dir = 4
                            if self.angle > 225 and self.angle < 315:
                                self.dir = 3

            if self.dir != None:
                if self.dir == 1:
                    self.rect.centerx -= self.speed
                    for i in stoppers:
                        for wall in i:
                            if self.rect.colliderect(wall[1]):
                                self.rect.left = wall[1].right + self.spacer
                                self.dir = None
                if self.dir == 2:
                    self.rect.centerx += self.speed
                    for i in stoppers:
                        for wall in i:
                            if self.rect.colliderect(wall[1]):
                                self.rect.right = wall[1].left + self.spacer
                                self.dir = None
                if self.dir == 3:
                    self.rect.centery += self.speed
                    for i in stoppers:
                        for wall in i:
                            if self.rect.colliderect(wall[1]):
                                self.rect.bottom = wall[1].top + self.spacer
                                self.dir = None

                if self.dir == 4:
                    self.rect.centery -= self.speed
                    for i in stoppers:
                        for wall in i:
                            if self.rect.colliderect(wall[1]):
                                self.rect.top = wall[1].bottom + self.spacer
                                self.dir = None
            if self.rect.colliderect(pressure_tile[1]):
                self.rect.center = pressure_tile[1].center
                self.complete = True

        return self.complete
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # pygame.draw.rect(surface, constants.BLUE, self.rect)



