from util import *


SPEED = 600

class Projectile(pg.sprite.Sprite):
    def __init__(self, world, pos, dir, attacker):
        super().__init__(world.unplanet, world.projectiles)
        self.world = world
        self.plr = attacker==self.world.player
        self.pos = vec2(pos)
        self.init = pos
        self.frames = world.imgs[('blue_ball','projectile')[self.plr]]
        self.angle = 0
        self.dir = dir
        self.radius = self.frames[0].get_width() / 2
        self.velocity = dir * SPEED * BALLSPEED[(0,self.world.player.powerups[2])[self.plr]]

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
            if self.plr:
                # mob collision
                for mob in planet.mobs:
                    if mob.rect.colliderect(self.rect):
                        mob.damage(DAMAGE[self.world.player.powerups[3]])
                        if not self.world.player.powerups[5]: self.die(); return
            # player collision
            elif self.world.player.rect.colliderect(self.rect):
                self.world.player.damage(1)
                self.die(); return

            # planet collision
            if planet.center.distance_to(self.pos) < planet.radius + self.radius:
                self.die(); return
            
        # projectile collision
        for p in self.world.projectiles:
            if p.plr!=self.plr and self.pos.distance_to(p.pos) <= self.image.get_width():
                p.die()
                self.die()
                return
            
    def die(self):
        if self.pos.distance_to(self.init) > 50:
            sounds.boom.play()
            for _ in range(6):
                self.world.boom_pc.new(is_player=self.plr, color=proba(2), pos=self.pos, dir=-self.velocity.rotate(randint(-90,90)) * (randint(5,15)/10))
        self.kill()

    def draw(self):
        self.world.display.blit(self.image, self.rect.topleft - self.world.offset)