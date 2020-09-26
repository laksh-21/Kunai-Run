import pygame as pg
from sprites import *
import sys
from os import path
from settings import *
from tilemap import *
import random


game_folder                       = path.dirname(__file__)
image_folder                      = path.join(game_folder  , 'Images' )
map_folder                        = path.join(game_folder  , 'Map'    )
player_folder                     = path.join(image_folder , 'Player' )
zombie_folder                     = path.join(image_folder , 'Zombies')
z_male_folder                     = path.join(zombie_folder, 'male'   )
z_female_folder                   = path.join(zombie_folder, 'female' )
items_folder                      = path.join(image_folder , 'Items'  )
music_folder                      = path.join(game_folder  , 'Music'  )

class Game:
    def __init__(self):
        pg.init()
        self.screen         = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock          = pg.time.Clock()
        pg.key.set_repeat(250)
        self.load_data()
        self.start_time     = pg.time.get_ticks()
        self.level          = 1
        self.totalLevels    = 1
        self.paused         = False

    def load_data(self):
        self.item_images                  = {}

        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(items_folder, ITEM_IMAGES[item])).convert_alpha()
        
        self.player_idle_sprites          = [pg.image.load(path.join(player_folder, 'Idle__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.player_walk_sprites          = [pg.image.load(path.join(player_folder, 'Run__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.player_jump_sprites          = [pg.image.load(path.join(player_folder, 'Jump__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.player_dead_sprites          = [pg.image.load(path.join(player_folder, 'Dead__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.player_throw_sprites         = [pg.image.load(path.join(player_folder, 'Throw__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.player_jump_throw_sprites    = [pg.image.load(path.join(player_folder, 'Jump_Throw__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.shuriken_image               =  pg.image.load(path.join(player_folder, 'Kunai.png')).convert_alpha()
        self.zombie_male_walk_sprites     = [pg.image.load(path.join(z_male_folder, 'walk__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.zombie_female_walk_sprites   = [pg.image.load(path.join(z_female_folder, 'walk__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.zombie_male_dead_sprites     = [pg.image.load(path.join(z_male_folder, 'dead__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.zombie_female_dead_sprites   = [pg.image.load(path.join(z_female_folder, 'dead__00{i}.png'.format(i=i))).convert_alpha() for i in range(10)]
        self.zombie_male_attack_sprites   = [pg.image.load(path.join(z_male_folder, 'attack__{i}.png'.format(i=i))).convert_alpha() for i in range(1,11)]
        self.zombie_female_attack_sprites = [pg.image.load(path.join(z_female_folder, 'attack__{i}.png'.format(i=i))).convert_alpha() for i in range(1,11)]
        self.dim_screen                   = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        pg.mixer.music.set_volume(0.09)
        

    def new(self):
        self.map         = TileMap(path.join(map_folder, 'Level{}.tmx'.format(self.level)))
        self.map_img     = self.map.make_map()
        self.map_rect    = self.map_img.get_rect()
        self.all_sprites = pg.sprite.Group()
        self.walls       = pg.sprite.Group()
        self.zombies     = pg.sprite.Group()
        self.shurikens   = pg.sprite.Group()
        self.zwalls      = pg.sprite.Group()
        self.items       = pg.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'Player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'Wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'Zombie':
                gender = random.choice(['male', 'female'])
                Zombie(self, obj_center.x, obj_center.y, gender)
            if tile_object.name == 'ZWall':
                ZObstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name in ITEM_LIST:
                Item(self, obj_center, tile_object.name)
            
        self.camera = Camera(self.map.width, self.map.height)
        self.paused = False
    
    def run(self):
        self.playing = True

        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS)/500
            self.event()
            if not self.paused:
                self.update()
            
            self.draw()
        
    def quit(self):
        pg.quit()
        sys.exit()

    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Zombie) or isinstance(sprite, Player):
                sprite.draw_health_bar()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        
        self.draw_text("Blades Left: {blades}".format(blades=self.player.shurikens), "freesansbold.ttf", 22, LIGHTGREY, 870, 5)

        self.draw_text("Level: {blades}".format(blades=self.level), "freesansbold.ttf", 22, LIGHTGREY, 475, 5)
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("PAUSED", "freesansbold.ttf", 64, (200, 10, 10), WIDTH//2, HEIGHT//2, "center")
            self.draw_text("Press 'p' to continue or 'esc' to exit", "freesansbold.ttf", 20, (200, 10, 10), WIDTH//2, HEIGHT//2 + 80, "center")
        pg.display.flip()

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_p:
                    self.paused = not self.paused

    def show_title_screen(self):
        pass

    def show_end_screen(self):
        pass


game = Game()
game.show_title_screen()
while(True):
    game.new()
    game.run()
    # game.level += 1
    # if game.level > game.totalLevels:
    #     break
    game.show_end_screen()
