from mob import Mob
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
        self.imgs = world.imgs['player']
        
        self.planet: Planet = None
        self.ground = False
        self.velocity = vec2()
        self.tangent = vec2()
        self.side = 'R'

        self.inventory = {}

        self.select = self.hover = None
        self.breaking = None

        self.health = self.max_health = 6

        self.timers = {
            "attack": Timer(150)
        }

    def angle(self):
        return self.planet.get_polar()[1] if self.ground else -1
    
    def event(self, e):
        if e.type == pg.KEYDOWN and e.key == pg.K_LSHIFT and self.ground:
            sounds.switch_planet.play()
            d,a = self.planet.get_polar()
            self.planet.set_polar(d,a+180)

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
        self.force = self.planet.mass * vec
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
        for obj in self.world.objects:
            if obj.rect.collidepoint(self.world.mouse_world_pos):
                self.hover = obj
                if obj.pos.distance_to(self.pos) <= INTERACT_RANGE:
                    self.select = obj
                    if obj != old_select:
                        sounds.select.play()
                break
    
    def shoot(self):
        if self.world.mouse[0] and not self.timers["attack"]:
            self.timers["attack"].activate()
            sounds.shoot.play()
            vec = self.world.mouse_world_pos - self.rect.center
            vec = vec.normalize() if vec.magnitude() else VECTOR
            if self.ground and vec.dot(self.planet.vector()) < 0:
                tangent = self.planet.vector().normalize().rotate(90) * vec.magnitude()
                vec = tangent*(-1,1)[vec.dot(tangent) > 0]
            Projectile(self.world, self.rect.center, vec)

    def damage(self, x=1):
        sounds.plr_hit.play()
        self.health -= x
        if self.health <= 0:
            self.health = 0
            sounds.plr_die.play()
            self.kill()
            self.world.dead_timer.activate()

    def update(self):
        self.movement()
        self.interaction()
        self.shoot()
        for t in self.timers.values(): t.update()

    def draw(self):
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
        self.world.display.blit(h, h.get_rect(center=self.rect.midtop + vec2(0,-4*SCALE) - self.world.offset))
