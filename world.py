import random
from mob import Mob
from overlay import Overlay
from util import *
from planet import Planet
from player import Player
from prop import Prop


class World:
    def __init__(self, game):
        self.game = game
        self.display = game.screen
        self.render = game.world_render
        self.font = game.font
        self.paused = False

        # values
        self.offset = vec2()
        self.mouse_pos = self.mouse_world_pos = vec2()
        self.dead_timer = Timer(500, self.load_space)

        # images
        self.load_imgs()

        # map
        self.props = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.objects = pg.sprite.Group()
        self.unplanet = pg.sprite.Group()
        self.load_space()

        # overlay
        self.overlay = Overlay(self)

    def open(self):
        return#{sounds.music("world2.ogg")

    def load_imgs(self):
        projectile = load("particles/projectile",SCALE)
        plr_ts = load_tileset("player", (13,11))

        self.imgs = {
            "cursor": load_tileset("ui/cursor", (7,7)),
            **{name: {0: (image,outline(image))} for name,image in load_folder_dict("props").items()},
            "player": {0: {
                **sides("idle", plr_ts[0:2]),
                **sides("move", plr_ts[4:7]),
                **sides("jump", [plr_ts[2]]),
                **sides("fall", [plr_ts[3]]),
            }},
            "slime": {0: {
                **sides("idle", plr_ts[8:10], with_outline=True),
                **sides("move", plr_ts[12:15], with_outline=True),
            }},
            "rocket": {0: {
                **sides("move", load_tileset("rocket",(16,11)), with_outline=True),
            }},
            "projectile": [pg.transform.rotate(projectile,angle) for angle in range(360)],
            "health": load_tileset("ui/health", (7,6)),
            "plr_health": load_tileset("ui/plr_health", (7,6)),
        }

        for angle in range(1,360):
            self.imgs["player"][angle] = {status: [pg.transform.rotate(img, -angle) for img in frames] for status, frames in self.imgs["player"][0].items()}
            for mob in MOBS:
                self.imgs[mob][angle] = {status: [(pg.transform.rotate(i, -angle),pg.transform.rotate(o, -angle)) for i,o in frames] for status, frames in self.imgs[mob][0].items()}
            
    def load_space(self):
        for x in self.objects: x.kill()
        for x in self.unplanet: x.kill()

        self.player = Player(self, (0,-200))
        self.planets: list[Planet] = [Planet(self, (0,0), 200, True)]

        while len(self.planets) < 1000:
            MAPSIZE = 10000
            center = (randint(-MAPSIZE, MAPSIZE),randint(-MAPSIZE, MAPSIZE))
            radius = randint(100,500)
            for p in self.planets:
                distance = p.center.distance_to(center)
                if distance < (radius + p.radius)+50:
                    break
            else:
                self.planets.append(Planet(self, center, radius))
    
    def event(self, e):
        self.player.event(e)
        self.overlay.event(e)

    def compute_offset(self):
        camspeed = 10
        pos = (self.player.planet.center+3*self.player.pos)/4 if self.player.ground else self.player.pos
        offset = pos - vec2(W//2,H//2)
        self.offset.x += (offset.x - self.offset.x) / camspeed
        self.offset.y += (offset.y - self.offset.y) / camspeed
        self.mouse_world_pos = self.mouse_pos + self.offset
        self.viewport = pg.Rect(self.offset, (W,H))
        self.visible_planets = tuple(filter(lambda p: p.is_visible(), self.planets))

    def update(self):
        self.dead_timer.update()
        
        # Values
        self.dt = self.game.dt
        self.keys, self.mouse = pg.key.get_pressed(), pg.mouse.get_pressed()
        self.mouse_pos = vec2(pg.mouse.get_pos())
        self.compute_offset()

        # Update
        for planet in self.visible_planets: planet.update()
        for obj in self.unplanet: obj.update()

        # Overlay
        self.overlay.update()
        
    def draw_cursor(self):
        cursor = self.imgs['cursor'][bool(self.player.hover) + bool(self.player.select)]
        self.display.blit(cursor, cursor.get_rect(center=self.mouse_pos))

        if self.player.select:
            self.display.blit(*textr(self.player.select.type, self.font, 'white',
                bottomleft=self.mouse_pos+vec2(6,-6)))

    def draw(self):
        self.display.fill("black")

        for planet in self.visible_planets: planet.draw()
        for obj in self.unplanet: obj.draw()

        self.overlay.draw()
        self.draw_cursor()
