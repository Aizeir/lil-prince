import random
from mob import Mob
from overlay import Overlay
from powerup import Powerup
from util import *
from planet import Planet
from player import Player
from prop import Prop
import particle


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

        def die():
            if self.player.lives > 0:
                self.player.respawn()
            else:
                self.load_space()
        self.dead_timer = Timer(600, die)

        # images
        self.load_imgs()
        self.load_particles()

        # map
        self.props = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.objects = pg.sprite.Group()
        self.unplanet = pg.sprite.Group()
        self.interacts = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.planets: list[Planet] = []
        self.load_space()

        # overlay
        self.overlay = Overlay(self)

    def open(self):
        sounds.music("music.wav", volume=.6)

    def load_imgs(self):
        projectile = load("particles/projectile",SCALE)
        blue_ball = load("particles/blue_ball",SCALE)
        shooter_ts = load_tileset("shooter",(13,13))
        plr_ts = load_tileset("player", (13,11))
        power_ts = load_tileset("powerups", (12,12))
        heal_ts = load_tileset("heal",(9,8))
        powbord = load_tileset("powerup_border",(16,16))
        grass = load_tileset("grass",(3,7))

        self.imgs = {
            "cursor": load_tileset("ui/cursor", (7,7)),
            **{name: {0: (image,prop_outline(image))} for name,image in load_folder_dict("props").items()},
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
            "shooter": {0: {
                **sides("idle", shooter_ts[:2], with_outline=True),
                **sides("shoot", [shooter_ts[2]], with_outline=True),
            }},
            "projectile": [pg.transform.rotate(projectile,angle) for angle in range(360)],
            "blue_ball": [pg.transform.rotate(blue_ball,angle) for angle in range(360)],
            "health": load_tileset("ui/health", (7,6)),
            "plr_health": load_tileset("ui/plr_health", (7,6)),
            "powerup": [(power_ts[i], power_ts[len(power_ts)//2+i]) for i in range(len(power_ts)//2)],
            "powerup_border": [[pg.transform.rotate(powbord[i],angle) for angle in range(360)] for i in (0,1)],
            "powerup_pc": powbord[2:],
            
            "heal": [(heal_ts[i], heal_ts[len(heal_ts)//2+i]) for i in range(len(heal_ts)//2)],
            "grass": [[pg.transform.rotate(img,-angle) for angle in range(360)] for img in grass],
        }

        for angle in range(1,360):
            self.imgs["player"][angle] = {status: [pg.transform.rotate(img, -angle) for img in frames] for status, frames in self.imgs["player"][0].items()}
            for mob in MOBS:
                self.imgs[mob][angle] = {status: [(pg.transform.rotate(i, -angle),pg.transform.rotate(o, -angle)) for i,o in frames] for status, frames in self.imgs[mob][0].items()}

    def load_particles(self):
        self.hit_pc = particle.Particle()
        self.hit_pc.draw(lambda p: particle.draw_circle(p,self))
        @self.hit_pc.update
        def update(p):
            p['radius'] -= self.dt * 16
            p['pos'] = p['pos'] + p['dir'] * self.dt
            if p['radius'] == 0: self.hit_pc.delete(p)


        pixel = pg.Surface((4,4)); pixels = [pg.transform.rotate(pixel, a) for a in range(360)]

        s_pixels = [(img,img.copy()) for img in pixels]
        for p1,p2 in s_pixels: p1.fill((0,87,132)); p2.fill((49,162,242))

        p_pixels = [(img,img.copy()) for img in pixels]
        for p1,p2 in p_pixels: p1.fill((190,38,51)); p2.fill((224,111,139))

        self.boom_pc = particle.Particle(angle=0, alpha=255)
        self.boom_pc.draw(lambda p: particle.draw_image(p,self))
        @self.boom_pc.update
        def update(p):
            p['alpha'] -= 500 * self.dt
            p['angle'] += 360 * self.dt
            p['image'] = ((s_pixels,p_pixels)[p['is_player']])[int(p['angle'] % 360)][p['color']]
            p['image'].set_alpha(p['alpha'])
            p['pos'] = p['pos'] + p['dir'] * self.dt
            p['dir'] = p['dir'] * 0.9
            if p['alpha'] <= 100: self.boom_pc.delete(p)
            for pl in self.visible_planets:
                if pl.center.distance_to(p['pos']) <= pl.radius:
                    self.boom_pc.delete(p)
                    break
        
        self.power_pc = particle.Particle(size=1,alpha=255)
        self.power_pc.draw(lambda p: particle.draw_image(p,self))
        @self.power_pc.update
        def update(p):
            p['size'] += 3 * self.dt
            img = self.imgs["powerup_pc"][0]
            p['image'] = pg.transform.scale_by(img,p['size'])
            p['alpha'] -= 500 * self.dt
            if p['alpha'] <= 100:
                self.power_pc.delete(p)
            else:
                p['image'].set_alpha(p['alpha'])
        
        self.implode_pc = particle.Particle(radius=4*SCALE,alpha=255)
        self.implode_pc.draw(lambda p: particle.draw_image(p,self))
        @self.implode_pc.update
        def update(p):
            p['alpha'] -= 500 * self.dt
            p['radius'] += IMPLODE_RANGE[self.player.powerups[7]-1] * self.dt
            img = pg.Surface((2*p["radius"], 2*p["radius"]))
            img.set_colorkey('black')
            img.set_alpha(p["alpha"])
            pg.draw.circle(img,(255,255,255),(p["radius"], p["radius"]),p["radius"])
            p['image'] = img
            if p['alpha'] <= 100:
                self.implode_pc.delete(p)
            else:
                p['image'].set_alpha(p['alpha'])
                for m in self.mobs:
                    if m.pos.distance_to(p['pos']) <= p['radius']+4*SCALE:
                        m.die()
    
    def load_space(self):
        # Clear old world
        for x in self.objects: x.kill()
        for x in self.unplanet: x.kill()
        self.planets.clear()
        MAPSIZE = 6000

        # Planets
        self.player = Player(self, (0,-200))
        self.planets = [Planet(self, (0,0), 200, True)]
        
        while len(self.mobs) < MAX_MOBS:
            center = (randint(-MAPSIZE, MAPSIZE),randint(-MAPSIZE, MAPSIZE))
            radius = randint(100,500)
            for p in self.planets:
                distance = p.center.distance_to(center)
                if distance < (radius + p.radius)+50:
                    break
            else:
                self.planets.append(Planet(self, center, radius))
        
        # Powerups
        POWER_MS = 5000
        powerups = []
        for i,n in enumerate(POWERUP_NUM): powerups.extend([(i,0)]*n)
        for i,n in enumerate(HEAL_NUM): powerups.extend([(i,1)]*n)
        
        
        shuffle(powerups)

        while powerups:
            pos = vec2(randint(-POWER_MS,POWER_MS),randint(-POWER_MS,POWER_MS))
            for p in self.planets:
                if p.center.distance_to(pos) < p.radius+50: break
            else:
                for p in self.powerups:
                    if p.pos.distance_to(pos) < 50: break
                else: 
                    Powerup(self, pos, *powerups.pop())

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
        particle.update()

        # Overlay
        self.overlay.update()
        
    def draw_cursor(self):
        cursor = self.imgs['cursor'][bool(self.player.hover) + bool(self.player.select)]
        self.display.blit(cursor, cursor.get_rect(center=self.mouse_pos))

        if self.player.select:
            t,r = textr(self.player.select.type, self.font, 'white', bottomleft=self.mouse_pos+vec2(6,-6))
            out = outline(t,3,black)
            self.display.blit(out,out.get_rect(center=r.center))
            self.display.blit(t,r)

    def draw(self):
        self.display.fill((0,0,0))

        for planet in self.visible_planets: planet.draw()
        particle.draw()
        for obj in self.unplanet: obj.draw()

        self.overlay.draw()
        self.draw_cursor()

        # Render
        planets = [(*p.center, p.radius, p.type) for p in self.visible_planets]
        planets += [(0,0,0,0)]*(16-len(planets))
        render(self.game.screen, self.render,
            offset=self.offset,
            resolution=(W,H),
            planets=planets,
            planet_num=len(planets),
            time=pg.time.get_ticks(),
        )
