from prop import Prop
from util import *

RANGE = 40

class Mob(pg.sprite.Sprite):
    def __init__(self, planet, angle, type):
        super().__init__(planet.mobs, planet.world.mobs, planet.world.objects)
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
        
        self.health = self.max_health = 3
        self.attack_timer = Timer(300)

    def damage(self):
        sounds.hit.play()
        self.health -= 1
        if self.health == 0:
            self.die()

    def die(self):
        sounds.die.play()
        self.kill()

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
        self.move = 0
        if self.type == "slime" and self.planet == self.player.planet:
            if self.player.pos.distance_to(self.pos) > RANGE:
                self.move = (-1,1)[(self.angle + angle)%360 > 180]
        elif self.type == "rocket":
            self.move = self.def_move

        # Move
        self.angle += self.move
        self.pos = self.planet.center + VECTOR.rotate(self.angle) * self.planet.radius
        
        # Attack
        if not self.attack_timer and self.player.pos.distance_to(self.pos) <= RANGE:
            self.attack_timer.activate()
            if self.type == "slime":
                self.player.damage()
            elif self.type == "rocket":
                self.player.damage(2)
                self.die()

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
        h = self.world.imgs["health"][self.max_health-self.health]
        self.world.display.blit(h, h.get_rect(center=self.rect.midtop + vec2(0,-4*SCALE) - self.world.offset))
