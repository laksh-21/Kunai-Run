import pygame as pg
from settings import *
from random import choice
import pytweening as tween

vec = pg.math.Vector2

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect)

def distance(one, two):
    return (one.pos.x - two.pos.x)**2 + (one.pos.y - two.pos.y)**2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if isinstance(sprite, Zombie):
                    sprite.change_dir()
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                if isinstance(sprite, Zombie):
                    sprite.change_dir()
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                if isinstance(sprite, Player):
                    sprite.feet_on_ground = True
                    sprite.jumping = False
                    sprite.jump_count = 0
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game               = game
        self.image              = self.game.player_idle_sprites[0]
        self.rect               = self.image.get_rect()
        self.rect.center        = (x, y)
        self.vel                = vec(0, 0)
        self.pos                = vec(x,y)
        self.feet_on_ground     = True
        self.jumping            = False
        self.jump_count         = 0
        self.walk_count         = 0
        self.idle_count         = 0
        self.walking            = False
        self.throw_count        = 0
        self.throwing           = False
        self.facing_left        = False
        self.last_throw         = 0
        self.health             = PLAYER_HEALTH
        self.dead               = False
        self.dead_count         = 0
        self.last_damage_taken  = 0
        self.hit_rect           = PLAYER_HIT_RECT
        self.hit_rect.center    = self.rect.center
        self.shurikens          = 5

    def get_keys(self):
        self.vel.x  = 0
        keys        = pg.key.get_pressed()
        if keys[pg.K_RIGHT] and self.pos.x - 84 < 3070 and not self.throwing:
            self.walking        = True
            self.facing_left    = False
            self.vel.x          = PLAYER_SPEED
        elif keys[pg.K_LEFT] and self.pos.x > 0 and not self.throwing:
            self.walking        = True
            self.facing_left    = True
            self.vel.x          = -PLAYER_SPEED
        else:
            self.walking = False
        if keys[pg.K_UP] and self.feet_on_ground:
            self.vel.y          = JUMPFORCE.y
            self.feet_on_ground = False
            self.jumping        = True
        
        if keys[pg.K_LCTRL] or keys[pg.K_SPACE]:
            if pg.time.get_ticks() - self.last_throw > SHURIKEN_RATE and self.shurikens > 0:
                self.throwing   = True
                self.last_throw = pg.time.get_ticks()
                pos             = self.pos + SHURIKEN_OFFSET
                direction = 1
                if self.facing_left:
                    direction   = -1
                    pos         = self.pos
                Shuriken(self.game, pos, direction)
                self.shurikens -= 1
        else:
            if self.throw_count == 49:
                self.throwing    = False
                self.throw_count = 0

    def draw_health_bar(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        
        wd = 100 * (self.health / 100)
        self.health_bar = pg.Rect(10, 10, wd, 7)

        if self.health <= PLAYER_HEALTH:
            pg.draw.rect(self.game.screen, col, self.health_bar)
        

    def gravity(self):
        self.vel.y += (GRAVITY.y * self.game.dt)
    
    def death(self):
        self.dead_count += 1
        if self.dead_count < 60:
            self.image = self.game.player_dead_sprites[self.dead_count//6]
        else:
            self.image = self.game.player_dead_sprites[9]
        
        if self.dead_count >= 70:
            self.game.playing = False

    def collide_with_zombies(self):
        hits = pg.sprite.spritecollide(self, self.game.zombies, False, collide_hit_rect)
        if hits and pg.time.get_ticks() - self.game.start_time > 30 and (pg.time.get_ticks() - self.last_damage_taken > 500):
            for hit in hits:
                hit.vel.x = 0
                hit.attacking = True
            self.health -= ZOMBIE_DAMAGE
            self.last_damage_taken = pg.time.get_ticks()
            if self.facing_left:
                self.pos.x += 10
            else:
                self.pos.x -= 10
            self.vel.y = -100

    def collide_with_items(self):
        hits = pg.sprite.spritecollide(self, self.game.items, True, collide_hit_rect)
        
        for hit in hits:
            if hit.type == 'Blades':
                self.shurikens += 5

    def update(self):
        self.gravity()

        if self.health <= 0:
            self.dead = True

        if not self.dead:
            self.collide_with_zombies()
            self.collide_with_items()
            self.get_keys()

        if self.throwing:
            # THIS IS THE THROWING CONDITION
            self.throw_count = (self.throw_count + 1)%50
            if self.jumping:
                self.image = self.game.player_jump_throw_sprites[self.throw_count//5]
            else:
                self.image = self.game.player_throw_sprites[self.throw_count//5]
        elif self.jumping:
            # THIS IS THE JUMPING CONDITION
            self.jump_count = (self.jump_count + 1)
            index = 0
            if self.jump_count < 100:
                index = self.jump_count//10
            else:
                index  = 9
            self.image = self.game.player_jump_sprites[index]
        elif(self.walking):
            # THIS IS THE WALKING CONDITION
            self.walk_count = (self.walk_count + 1)%50
            self.image      = self.game.player_walk_sprites[self.walk_count//5]    
        else:
            # THIS IS THE IDLE CONDITION
            self.idle_count = (self.idle_count + 1)%50
            self.image      = self.game.player_idle_sprites[self.idle_count//5]
        
        if self.dead:
            self.vel.x = 0
            self.death()

        if self.facing_left:
            self.image = pg.transform.flip(self.image, True, False)
        
        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.pos               += self.vel * self.game.dt
        self.hit_rect.centerx   = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery   = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center        = self.hit_rect.center
        if self.vel.y > 0:
            self.feet_on_ground = False
        
        if self.pos.y > LEVELHEIGHT:
            self.dead = True


class Zombie(pg.sprite.Sprite):
    def __init__(self, game, x, y, gender):
        self.groups = game.all_sprites, game.zombies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game               = game
        self.image              = self.game.zombie_male_walk_sprites[0]
        self.rect               = self.image.get_rect()
        self.rect.center        = (x, y)
        self.vel                = vec(ZOMBIE_SPEED, 0)
        self.pos                = vec(x,y)
        self.feet_on_ground     = True
        self.walkCount          = 0
        self.facing_left        = False
        self.last_turn          = 0
        self.gender             = gender
        self.health             = ZOMBIE_HEALTH
        self.dead               = False
        self.dead_count         = 0
        self.attacking          = False
        self.attack_count       = 0
        self.hit_rect           = ZOMBIE_HIT_RECT.copy()
        self.hit_rect.center    = self.rect.center

    def move(self):
        self.walkCount = (self.walkCount + 1) % 100
        if pg.time.get_ticks() - self.last_turn > 200 and not self.dead:
            self.last_turn = pg.time.get_ticks()
            
            if distance(self, self.game.player) <= 400**2 and abs(self.pos.y - self.game.player.pos.y) < 10:
                if self.pos.x - self.game.player.pos.x > 0:
                    self.facing_left = True
                else:
                    self.facing_left = False
        
        if pg.sprite.spritecollideany(self, self.game.zwalls):
            self.change_dir()

    def gravity(self):
        self.vel.y += (GRAVITY.y * self.game.dt)

    def draw_health_bar(self):
        if self.health > 3/5 * ZOMBIE_HEALTH:
            col = GREEN
        elif self.health > 3/10 * ZOMBIE_HEALTH:
            col = YELLOW
        else:
            col = RED
        
        wd = int(60 * (self.health / 100))
        self.health_bar = pg.Rect(self.game.camera.x + self.pos.x - self.rect.width//2, self.game.camera.y + self.pos.y - self.rect.height//2, wd, 5)

        if self.health < ZOMBIE_HEALTH:
            pg.draw.rect(self.game.screen, col, self.health_bar)

    def change_dir(self):
        self.facing_left = not self.facing_left

    def death(self):
        self.dead_count += 1
        if self.dead_count < 60:
            if self.gender == 'male':
                self.image = self.game.zombie_male_dead_sprites[self.dead_count//6]
            else:
                self.image = self.game.zombie_female_dead_sprites[self.dead_count//6]
        else:
            if self.gender == 'male':
                self.image = self.game.zombie_male_dead_sprites[9]
            else:
                self.image = self.game.zombie_female_dead_sprites[9]
        
        if self.dead_count >= 70:
            self.kill()
    
    def jump(self):
        self.vel.y = -100

    def update(self):
        self.move()
        self.gravity()

        if self.health <= 0 and not self.dead:
            self.dead = True
            self.game.zombies.remove(self)
            self.vel  = vec(0, 0)

        self.walkCount = (self.walkCount + 1)%100
        if self.gender == 'male':
            self.image = self.game.zombie_male_walk_sprites[self.walkCount//10]
        else:
            self.image = self.game.zombie_female_walk_sprites[self.walkCount//10]    

        if self.attacking:
            self.attack_count += 1
            if self.attack_count < 50:
                if self.gender == 'male':
                    self.image    = self.game.zombie_male_attack_sprites[self.attack_count//5]
                else:
                    self.image    = self.game.zombie_female_attack_sprites[self.attack_count//5] 
            else:
                self.attacking    = False
                self.attack_count = 0
        else:
            if not self.dead:
                if self.facing_left:
                    self.vel.x = -ZOMBIE_SPEED
                else:
                    self.vel.x = ZOMBIE_SPEED
                
        if self.dead:
            self.death()
        
        if self.facing_left:
            self.image = pg.transform.flip(self.image, True, False)

        self.pos.x += self.vel.x * self.game.dt
        self.pos.y += self.vel.y * self.game.dt

        self.hit_rect.centerx   = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery   = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center        = self.hit_rect.center
        if self.vel.y > 0:
            self.feet_on_ground = False
        
        if self.pos.y > LEVELHEIGHT:
            self.dead           = True


class Shuriken(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self.groups      = game.all_sprites, game.shurikens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game        = game
        self.image       = self.game.shuriken_image
        self.rect        = self.image.get_rect()
        self.hit_rect    = self.rect
        self.pos         = vec(pos)
        self.rect.center = pos
        self.vel         = vec(SHURIKEN_SPEED, 0) * direction
        self.spawn_time  = pg.time.get_ticks()

        if direction == -1:
            self.image = pg.transform.flip(self.image, True, False)
            self.pos  += vec(-40, 0)

    
    def collide_with_zombies(self):
        hits = pg.sprite.spritecollide(self, self.game.zombies, False, collide_hit_rect)
        if hits:
            self.kill()
        for hit in hits:
            hit.health  -= SHURIKEN_DAMAGE
            hit.jump()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        
        self.collide_with_zombies()

        if pg.time.get_ticks() - self.spawn_time > SHURIKEN_RANGE:
            self.kill()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game   = game
        self.image  = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect   = self.image.get_rect()
        self.pos    = vec(x, y)
        self.rect.x = self.pos.x*TILESIZE
        self.rect.y = self.pos.y*TILESIZE


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups   = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game     = game
        self.rect     = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x        = x
        self.y        = y
        self.rect.x   = x
        self.rect.y   = y


class ZObstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups   = game.zwalls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game     = game
        self.rect     = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x        = x
        self.y        = y
        self.rect.x   = x
        self.rect.y   = y


class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, item_type):
        self.groups         = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game           = game
        self.image          = game.item_images[item_type]
        self.rect           = self.image.get_rect()
        self.type           = item_type
        self.pos            = pos
        self.rect.center    = pos
        self.tween          = tween.easeInOutSine
        self.step           = 0
        self.dir            = 1
        self.hit_rect       = self.rect

    def update(self):
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1
    