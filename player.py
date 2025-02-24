from mob import Mob
from powerup import Powerup
from projectile import Projectile
from prop import Prop
from util import *
from planet import Planet

JUMP_FORCE = 14
SPEED = 6

class Player(pg.sprite.Sprite):
    def __init__(self, world, pos):
        super().__init__(world.unplanet)
        self.world = world
        self.pos = vec2(pos)
        self.spawn = self.pos.copy()
        self.imgs = world.imgs['player']
        
        self.planet: Planet = None
        self.ground = False
        self.velocity = vec2()
        self.tangent = vec2()
        self.side = 'R'
        self.rect = pg.Rect(0,0,0,0)

        self.inventory = {}
        self.score = 0
        self.powerups = {i:0 for i in range(len(POWERUP_NUM))}

        self.select = self.hover = None
        self.breaking = None

        self.health = self.max_health = 6
        self.lives = 1

        def implode_done():
            self.notif("implode ready")
            sounds.done.play()

        self.timers = {
            "attack": Timer(FIRE_RATE[0]),
            "implode": Timer(IMPLODE_RELOAD[0], implode_done),
            "notif": Timer(1000),
        }

    @property
    def dead(self): return self.health == 0

    def notif(self, text):
        self.timers["notif"].activate()
        self.timers["notif"].text = text

    def angle(self):
        return self.planet.get_polar()[1] if self.ground else -1
    
    def event(self, e):
        if self.dead: return
        if e.type == pg.KEYDOWN and e.key == pg.K_LSHIFT and self.ground and self.powerups[6]:
            sounds.switch_planet.play()
            d,a = self.planet.get_polar()
            self.planet.set_polar(d,a+180)
        elif e.type == pg.MOUSEBUTTONDOWN and e.button == 3 and self.powerups[7] and not self.timers["implode"]:
            self.timers["implode"].activate()
            self.world.implode_pc.new(self.pos.copy())
            sounds.explosion.play()

        """elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and isinstance(self.select, Mob) and not self.timers['attack']:
            self.select.damage()
            self.timers['attack'].activate()"""
            
    def get_status(self):
        # Actioh
        if self.ground:
            self.action = ('idle','move')[bool(self.tangent)]
        else:
            self.action = ('jump','fall')[self.velocity.dot(self.force) > 0]
        # Side
        if self.move.x:
            self.side = "LR"[self.move.x > 0]
        # Status
        self.status = self.action + "_" + self.side

    def movement(self):
        # Get nearest planet
        for planet in self.world.planets:
            if not self.planet or planet.distance()-planet.radius < self.planet.distance()-self.planet.radius:
                if planet != self.planet:
                    sounds.switch_planet.play()
                self.planet = planet
        # Apply gravity
        vec = -self.planet.vector().normalize()
        self.force = self.planet.mass * vec * GRAVITY[self.powerups[4]]
        self.velocity += self.force
        
        # Jump
        if self.world.keys[pg.K_SPACE] and self.ground:
            sounds.jump.play()
            self.velocity = -vec * JUMP_FORCE

        # Tangent movement
        self.tangent = vec2()
        dx = (iskeys(self.world.keys, K_RIGHT) - iskeys(self.world.keys, K_LEFT))
        dy = (iskeys(self.world.keys, K_DOWN) - iskeys(self.world.keys, K_UP))
        self.move = vec2(dx,dy)
        u_t = vec.rotate(90)

        # Mvt en l'air
        if not self.ground:
            self.tangent = self.move * SPEED
        # Mvt ground
        # elif abs(u_t.dot(move)) >= .05:
        #     self.tangent = u_t * SPEED * (-1,1)[u_t.dot(move) > 0]"""
        elif self.move.x:
            self.tangent = u_t * SPEED * (-1,1)[self.move.x < 0]

        # Move
        self.pos += self.velocity + self.tangent

        # On ground
        if self.planet.distance() <= self.planet.radius:
            if not self.ground: sounds.land.play(); sounds.switch_planet.stop()
            distance, angle = self.planet.get_polar()
            distance = self.planet.radius
            self.ground = True
            self.velocity = vec2()
            self.planet.set_polar(distance, angle)
        else:
            self.ground = False

    def interaction(self):
        # Prop selection
        old_select = self.select
        self.select = self.hover = None
        for obj in self.world.interacts:
            if obj.rect.collidepoint(self.world.mouse_world_pos):
                self.hover = obj
                if obj.pos.distance_to(self.pos) <= INTERACT_RANGE or isinstance(obj, Powerup):
                    self.select = obj
                    if obj != old_select:
                        sounds.select.play()
                break
        
        # Powerup
        for powerup in self.world.powerups:
            if powerup.rect.colliderect(self.rect):
                powerup.take()
                
    def shoot(self):
        if self.world.mouse[0] and not self.timers["attack"]:
            self.timers["attack"].activate()
            sounds.shoot.play()

            vec = self.world.mouse_world_pos - self.rect.center
            vec = vec.normalize() if vec.magnitude() else VECTOR
            if self.ground and vec.dot(self.planet.vector()) < 0:
                tangent = self.planet.vector().normalize().rotate(90) * vec.magnitude()
                vec = tangent*(-1,1)[vec.dot(tangent) > 0]
            Projectile(self.world, self.rect.center, vec, self)

            if self.powerups[0]:
                vec = -vec
                if self.ground and vec.dot(self.planet.vector()) < 0:
                    tangent = self.planet.vector().normalize().rotate(90) * vec.magnitude()
                    vec = tangent*(-1,1)[vec.dot(tangent) > 0]
                Projectile(self.world, self.rect.center, vec, self)

    def damage(self, x=1):
        sounds.plr_hit.play()
        self.health -= x
        if self.health <= 0:
            self.health = 0
            sounds.plr_die.play()
            self.lives -= 1
            self.world.dead_timer.activate()

            n = self.max_health * 3
            for i in range(n):
                angle = int(i/n*360)
                type = 1
                self.world.hit_pc.new(pos=self.pos, dir=(VECTOR*(200,500)[type]).rotate(randint(angle-20,angle+20)), color=PARTICLE_COLORS['player'][type],radius=randint(6,12))

        else:
            n = randint(3, 5)
            for i in range(n):
                angle = int(i/n*360)
                type = proba(2)
                self.world.hit_pc.new(pos=self.pos, dir=(VECTOR*(200,500)[type]).rotate(randint(angle-20,angle+20)), color=PARTICLE_COLORS['player'][type],radius=randint(6,12))

    def respawn(self):
        self.health = self.max_health
        for t in self.timers.values():
            t.deactivate()

    def knockback(self, dir, force=20):
        self.velocity += dir * force

    def update(self):
        if self.dead: return
        self.movement()
        self.interaction()
        self.shoot()
        for t in self.timers.values(): t.update()

    def draw(self):
        if self.dead: return
        # Values
        self.get_status()
        angle = int(-self.planet.vector().angle_to(VECTOR)) % 360

        # Image
        frames = self.imgs[angle][self.status]
        self.image = frames[frame_time(0,ANIM_SPEED,len(frames))]

        # Rect
        rect0 = self.imgs[0][self.status][0].get_rect(center=(0,0))
        point = vec2(rect0.midbottom).rotate(angle)
        self.rect = self.image.get_rect(center=self.pos - point + self.force.normalize()*SCALE)

        # Draw
        self.world.display.blit(self.image, self.rect.topleft - self.world.offset)

        # Health
        h = self.world.imgs["plr_health"][self.max_health-self.health]
        hr = h.get_rect(center=self.rect.midtop + vec2(0,-4*SCALE) - self.world.offset)
        self.world.display.blit(h, hr)

        # Notif
        if self.timers["notif"]:
            t = self.timers["notif"].text
            t,r = textr(t, self.world.font, "white", midbottom=self.rect.midtop + vec2(0,-10*SCALE) - self.world.offset)
            out = outline(t, 3, black)
            x = 1 - self.timers["notif"].percent(1)**.4 * .3
            t.set_alpha(x*255)
            self.world.display.blit(out, out.get_rect(center=r.center))
            self.world.display.blit(t,r)
