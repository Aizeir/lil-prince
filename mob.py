from projectile import Projectile
from prop import Prop
from util import *

RANGE = 40
MOB_HEALTH = {
    "slime":3,
    "rocket":2,
    "shooter":3,
}

class Mob(pg.sprite.Sprite):
    def __init__(self, planet, angle, type):
        super().__init__(planet.mobs, planet.world.mobs, planet.world.objects, planet.world.interacts)
        self.world, self.player = planet.world, planet.player
        self.imgs = planet.world.imgs[type]
        
        self.type = type
        self.planet = planet
        self.angle = angle
        self.pos = self.planet.center + VECTOR.rotate(self.angle) * self.planet.radius
        self.rect = pg.Rect(0,0,0,0)
        self.side = 'R'
        self.move = 0
        if type == 'rocket':
            self.def_move = 2 * choice((1,-1))
        
        self.health = self.max_health = MOB_HEALTH[type]
        self.attack_timer = Timer(300 if self.type != "shooter" else 1000)

    def damage(self,x):
        sounds.hit.play()
        self.health -= x
        if self.health <= 0:
            self.health = 0
            self.die()
        
        n = randint(3, 5)
        for i in range(n):
            angle = int(i/n*360)
            self.world.hit_pc.new(pos=self.pos, dir=(VECTOR*200).rotate(randint(angle-20,angle+20)), color=PARTICLE_COLORS[self.type][0],radius=randint(6,12))
    
    def die(self, sound=True):
        if sound: sounds.die.play()
        self.kill()
        self.world.player.score += 1
        
        n = self.max_health * 2
        for i in range(n):
            angle = int(i/n*360)
            self.world.hit_pc.new(pos=self.pos, dir=(VECTOR*500).rotate(randint(angle-20,angle+20)), color=PARTICLE_COLORS[self.type][1],radius=randint(6,12))

    def get_status(self):
        # Action
        if self.type == "rocket":
            self.action = "move"
        else:
            self.action = ('idle','move')[self.move!=0]
        # Side
        if self.move: self.side = "LR"[self.move > 0]
        # Status
        self.status = self.action + "_" + self.side

    def update(self):
        if self.player.health == 0: return
        self.attack_timer.update()
        angle = self.player.angle()

        # Get movement
        if self.type == "slime" and self.planet == self.player.planet and self.player.pos.distance_to(self.pos) > RANGE:
            self.move = (-1,1)[(self.angle + angle)%360 > 180]
        elif self.type == "rocket":
            self.move = self.def_move
        else:
            self.move = 0
        # Move
        if self.move:
            self.angle += self.move
            self.pos = self.planet.center + VECTOR.rotate(self.angle) * self.planet.radius
        
        # Attack
        if not self.attack_timer and self.player.pos.distance_to(self.pos) <= RANGE:
            self.attack_timer.activate()
            if self.type == "slime":
                self.player.damage()
            elif self.type == "rocket":
                self.player.damage(2)
                self.player.knockback(self.planet.vector(self).rotate(90 * int(self.def_move/abs(self.def_move))).normalize())
                sounds.rocket.play()
                self.die(False)
        if not self.attack_timer and self.type == "shooter" and self.player.pos.distance_to(self.pos) <= 500:
            self.attack_timer.activate()

            vec = self.world.player.pos - self.rect.center
            vec = vec.normalize() if vec.magnitude() else VECTOR
            if vec.dot(self.planet.vector(self)) < 0:
                tangent = self.planet.vector(self).normalize().rotate(90) * vec.magnitude()
                vec = tangent*(-1,1)[vec.dot(tangent) > 0]
            Projectile(self.world, self.rect.center, vec, self)

    def draw(self):
        # Values
        self.get_status()
        vec = self.planet.vector(self)
        angle = int(self.angle % 360)

        # Image
        frames = self.imgs[angle][self.status]
        self.image, self.outline = frames[frame_time(0,ANIM_SPEED,len(frames))]
               
        # Rect
        rect0 = self.imgs[0][self.status][0][0].get_rect(center=(0,0))
        point = vec2(rect0.midbottom).rotate(angle)
        self.rect = self.image.get_rect(center=self.pos - point - vec.normalize()*SCALE)
        self.rect_outline = self.outline.get_rect(center=self.pos - point - vec.normalize()*SCALE)
        
        # draw
        if self.world.player.select == self:
            self.world.display.blit(self.outline, self.rect_outline.topleft - self.world.offset)
        self.world.display.blit(self.image, self.rect.topleft - self.world.offset)
            
        # Health
        h = self.world.imgs["health"][self.max_health-math.ceil(self.health)]
        self.world.display.blit(h, h.get_rect(center=self.rect.midtop + vec2(0,-4*SCALE) - self.world.offset))
