from util import *


class Overlay:
    def __init__(self, world):
        self.world = world
        self.display = world.display
        self.font = font("font.ttf", 60)
        self.font2 = font("font.ttf", 40)
        self.powerup = [[pg.transform.scale(i,(18*SCALE,18*SCALE)) for i in frames] for frames in self.world.imgs['powerup']]

    def event(self,e):
        pass
    
    def update(self):
        pass

    def draw(self):
        # Score
        text, rect = textr(f"killed: {self.world.player.score}/{len(self.world.mobs)+self.world.player.score}",self.font, 'white', topleft=(40,30))
        out = outline(text, 4,black)
        self.display.blit(out,out.get_rect(center=rect.center))
        self.display.blit(text,rect)

        # Health
        text, rect = textr(f"health: {self.world.player.health}/{self.world.player.max_health}",self.font, 'white', topleft=(40,70))
        out = outline(text, 4,black)
        self.display.blit(out,out.get_rect(center=rect.center))
        self.display.blit(text,rect)
        
        # Lives
        text, rect = textr(f"lives: {self.world.player.lives}",self.font, 'white', topleft=(40,110))
        out = outline(text, 4,black)
        self.display.blit(out,out.get_rect(center=rect.center))
        self.display.blit(text,rect)

        # Powerups (origin topleft)
        x,y = 40,190
        for p,n in self.world.player.powerups.items():
            if n==0: continue

            img = self.powerup[p][frame_time(0,ANIM_SPEED,2)]
            out = outline(img, 2*SCALE, black)
            rect = img.get_rect(topleft=(x,y))

            if p == 7 and self.world.player.timers["implode"]:
                x = self.world.player.timers["implode"].percent(1) **.5 * .8
                y = x * rect.h
                img = self.powerup[p][1].copy()
                img.fill((50,50,50), special_flags=pg.BLEND_RGB_SUB)
                img.fill((150,150,150), rect=(0,0,rect.w,rect.h-y), special_flags=pg.BLEND_RGB_SUB)
            
            #self.display.blit(out, out.get_rect(center=rect.center))
            self.display.blit(img, rect)


            if POWERUP_NUM[p] > 1:
                t,r = textr(f"{n}/{POWERUP_NUM[p]}", self.font2, "white", center=rect.midbottom)
                out = outline(t, 2, black)
                self.display.blit(out, out.get_rect(center=r.center))
                self.display.blit(t, r)

            # name
            t,r = textr(POWERUP_NAMES[p], self.font2, "white", midleft=rect.midright+vec2(10,0))
            out = outline(t, 2, black)
            self.display.blit(out, out.get_rect(center=r.center))
            self.display.blit(t, r)

            y += 80
