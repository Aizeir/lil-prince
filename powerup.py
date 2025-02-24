from util import *


SPEED = 600
class Powerup(pg.sprite.Sprite):
    def __init__(self, world, pos, idx, heal):
        super().__init__(world.unplanet, world.interacts, world.powerups)
        self.world = world
        self.player = world.player
        self.pos = vec2(pos)
        self.idx = idx
        self.is_heal = heal
        self.type = POWERUP_NAMES[idx] if not heal else ('+1 health','+1 life')[idx]
        self.frames = world.imgs['powerup' if not heal else 'heal'][idx]
        self.rect = self.image.get_rect(center=self.pos)

    @property
    def image(self):
        return self.frames[frame_time(0, ANIM_SPEED, len(self.frames))]

    def update(self): return
    
    def take(self):
        self.kill()
        
        # Heal powerups
        if self.is_heal:
            self.player.notif(self.type)
            if self.idx == 0:
                sounds.heal.play()
                self.player.health = max(self.player.max_health, self.player.health + 1)
            else:
                sounds.life.play()
                self.player.lives += 1
            return
        
        # Actual powerups
        sounds.powerup_2.play()
        sounds.powerup.play()
        self.world.power_pc.new(self.pos)
        self.player.powerups[self.idx] += 1

        # fire rate
        if self.idx == 1: 
            self.player.timers['attack'].duration = FIRE_RATE[self.player.powerups[1]]
            self.player.timers['attack'].deactivate()
        # implode (reload time)
        elif self.idx == 7: 
            self.player.timers['implode'].duration = IMPLODE_RELOAD[self.player.powerups[7]-1]*1000
            self.player.timers['implode'].deactivate()

    def draw(self):
        border = self.world.imgs['powerup_border'][self.player.select==self][frame_time(0, 100, 360)]
        self.world.display.blit(border, border.get_rect(center=self.rect.center).topleft - self.world.offset)
        self.world.display.blit(self.image, self.rect.topleft - self.world.offset)