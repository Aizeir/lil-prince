from util import *


class Prop(pg.sprite.Sprite):
    def __init__(self, planet, angle, type):
        super().__init__(planet.props, planet.world.props, planet.world.objects)
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