from util import *


SPEED = 600
class Projectile(pg.sprite.Sprite):
    def __init__(self, world, pos, dir):
        super().__init__(world.unplanet)
        self.world = world
        self.pos = vec2(pos)
        self.init = pos
        self.frames = world.imgs['projectile']
        self.angle = 0
        self.dir = dir
        self.radius = self.frames[0].get_width() / 2
        self.velocity = dir * SPEED

    @property
    def image(self): return self.frames[int(self.angle%360)]
    @property
    def rect(self): return self.image.get_rect(center=self.pos)

    def update(self):
        # angle
        self.angle += 360 * self.world.dt

        # movement
        """for planet in self.world.planets:
            force = -planet.vector(self) * planet.radius / planet.center.distance_to(self.pos) * .001
            self.velocity += force"""

        self.pos += self.velocity * self.world.dt

        # too far
        if self.pos.distance_to(self.init) > 2*W: self.kill()

        # collision
        for planet in self.world.planets:
            # mob collision
            for mob in planet.mobs:
                if mob.rect.colliderect(self.rect):
                    mob.damage()
                    self.die(); return
            # planet collision
            if planet.center.distance_to(self.pos) < planet.radius + self.radius:
                self.die(); return
            
    def die(self):
        if self.pos.distance_to(self.init) > 50:
            sounds.boom.play()
        self.kill()

    def draw(self):
        self.world.display.blit(self.image, self.rect.topleft - self.world.offset)