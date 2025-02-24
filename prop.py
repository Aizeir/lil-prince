from util import *


class Prop(pg.sprite.Sprite):
    def __init__(self, planet, angle, type):
        super().__init__(planet.props, planet.world.props, planet.world.objects, planet.world.interacts)
        self.planet = planet
        self.world = planet.world
        self.pos:vec2 = planet.center + (VECTOR*(planet.radius-SCALE)).rotate(angle)
        self.angle = angle
        self.type = type

        # Image
        if angle not in self.world.imgs[type]:
            self.world.imgs[type][angle] = [pg.transform.rotate(self.world.imgs[type][0][s], -angle) for s in (0,1)]
        self.image, self.outline = self.world.imgs[self.type][self.angle]
        
        # Rect
        rect0 = self.world.imgs[self.type][0][0].get_rect(center=(0,0))
        point = vec2(rect0.midbottom).rotate(self.angle)
        self.rect = self.image.get_rect(center=self.pos-point)
        self.rect_outline = self.outline.get_rect(center=self.pos-point)

    def draw(self):
        # Outline
        if self.world.player.select == self:
            self.world.display.blit(self.outline, self.rect_outline.topleft - self.world.offset)
        # Image
        self.world.display.blit(self.image, self.rect.topleft - self.world.offset)



GRASS_RANGE = 16*SCALE
class Grass(pg.sprite.Sprite):
    def __init__(self, planet, angle):
        super().__init__(planet.grass, planet.world.props, planet.world.objects)
        self.planet = planet
        self.world = planet.world
        self.pos:vec2 = planet.center + (VECTOR*(planet.radius-SCALE)).rotate(angle)
        self.angle = angle
        self.type = 'gress'
        self.idx = self.planet.type * 3 + randint(0,2)
        self.angle_off = 0
        self.update_image_rect()

    def update_image_rect(self):
        angle = int((self.angle - self.angle_off) % 360)
        self.image = self.world.imgs['grass'][self.idx][angle]
                
        rect0 = self.world.imgs["grass"][self.idx][0].get_rect(center=(0,0))
        point = vec2(rect0.midbottom).rotate(angle)
        self.rect = self.image.get_rect(center=self.pos-point)
    
    def update(self):
        off = 0
        plr = self.world.player
        mobs = self.planet.mobs
        if plr.planet == self.planet and plr.ground:
            mobs = (plr, *mobs)

        for mob in mobs:
            d = mob.pos.distance_to(self.pos)
            if d < GRASS_RANGE:
                mob_vect = self.planet.vector(mob)
                vect = self.planet.vector(self)
                off = math.copysign((GRASS_RANGE-d)/GRASS_RANGE * 90, mob_vect.dot(vect.rotate(90)))
                break

        if off != self.angle_off:
            self.angle_off = off
            self.update_image_rect()
    
    def draw(self):
        self.world.display.blit(self.image, self.rect.topleft - self.world.offset)
        