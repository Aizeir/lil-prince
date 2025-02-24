from random import choices
from mob import Mob
from prop import Grass, Prop
from util import *


class Planet:
    def __init__(self, world, center, radius, no_mob=False):
        self.world = world
        self.player = world.player
        self.center = vec2(center)
        self.radius = radius
        self.mass = .5
        self.type = randint(0,2)

        self.props = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.grass = pg.sprite.Group()
        self.generate(no_mob)

        self.rect = pg.Rect(center-vec2(radius,radius), (2*radius, 2*radius)).inflate(40,40)

    def __repr__(self):
        return str(self.center)
    
    def generate(self, no_mob):
        for angle in range(0,360,18):
            x = randint(1,100)
            if x>=92 and not no_mob and len(self.world.mobs) < MAX_MOBS:
                Mob(self, angle, choices(MOBS, (1,1,.5))[0]); continue
            
            prop = None
            # Hot
            if self.type == 0:
                if x<=3: prop = "rock"
                elif x<=10: prop = "magma rock"
                elif x<=14: prop = "mushroom"
                elif x<=16: prop = "plant"
            # Warm
            elif self.type == 1:
                if x<=3: prop = "rock"
                elif x<=10: prop = "bush"
                elif x<=14: prop = "mushroom"
                elif x<=18: prop = "plant"
                elif x<=28: prop = choice(('tree','tall tree'))
            # Brown
            elif self.type == 2:
                if x<=3: prop = "rock"
                elif x<=10: prop = "crying rock"
                elif x<=15: prop = "mushroom"
                elif x<=18: prop = "plant"
                elif x<=22: prop = choice(('tree','tall tree'))

            if prop:
                Prop(self, angle, prop)

        for angle in range(0,360):
            if proba(60):
                for a in range(angle, angle+randint(10,30)):
                    if proba(5):
                        Grass(self, a)

    def distance(self):
        return self.center.distance_to(self.player.pos)
    
    def vector(self, mob=None) -> vec2:
        """ PLANETE > JOUEUR """
        return (mob or self.player).pos - self.center
    
    def get_polar(self):
        vec = self.vector()
        return vec.magnitude(), vec.angle_to(VECTOR)
    
    def set_polar(self, dist, angle):
        self.player.pos = self.center + VECTOR.rotate(-angle)*dist
    
    def is_visible(self):
        r = self.radius + 100
        if self.center.x + r < self.world.viewport.left: return False
        if self.center.x - r > self.world.viewport.right: return False
        if self.center.y + r < self.world.viewport.top: return False
        if self.center.y - r > self.world.viewport.bottom: return False
        return True
    
    def update(self):
        for grass in self.grass:   grass.update()
        for mob in self.mobs:   mob.update()
    
    def draw(self):
        for grass in self.grass: grass.draw()
        for prop in self.props: prop.draw()
        #pg.draw.circle(self.world.display, 'darkgray', self.center-self.world.offset, self.radius)
        #pg.draw.circle(self.world.display, 'gray', self.center-self.world.offset, self.radius, SCALE)
        for mob in self.mobs:   mob.draw()

