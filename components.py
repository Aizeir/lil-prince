from util import *

   
class Animation:
    def __init__(self, sprite, animation, status=None, on_anim_end=lambda:True, on_new_frame=lambda:None):
        """
        animation: {status: frames} ou image simple
        on_end: True = loop, None/False: laisser sur la dernière
        """
        self.sprite = sprite
        self.animation = animation
        self.status = status
        self.frame_idx = 0
        self.anim_speed = ANIM_SPEED

        # callbacks
        self.new_frame = on_new_frame
        self.end = on_anim_end
        
    @property
    def static(self): return isinstance(self.animation, pg.Surface)
    @property
    def image(self):  return self.animation if self.static else self.animation[self.status][int(self.frame_idx)]

    def set_status(self, status, always_reset=False):
        if always_reset or self.status != status:
            self.frame_idx = 0
        self.status = status
    
    def update(self):
        if self.static: return

        # Incrase frame idx
        old = self.frame_idx
        self.frame_idx += self.anim_speed * self.sprite.world.dt
        # New frame
        if int(self.frame_idx) > old:
            self.new_frame()
        # End of anim
        if self.frame_idx >= len(self.animation[self.status]):
            if self.end():
                self.frame_idx = 0
            else:
                self.frame_idx = len(self.animation[self.status])-1


class Movement:
    def __init__(self, sprite, collide_with=None):
        """ Agit sur hitbox, utilise "set_position" """
        self.sprite = sprite
        self.direction = vec2()
        self.collisions = {'L':[],'R':[],'T':[],'B':[],'all':[]}
        self.collide_with = collide_with
    
    @property
    def moving(self): return bool(self.direction)

    @staticmethod
    def obj_is_pushing(obj, dir):
        if not hasattr(obj, "movement"): return False
        if "x" in dir and obj.movement.direction.x:
            return abs(obj.movement.direction.x) > abs(obj.movement.direction.y) and (obj.movement.direction.x<0) == ('-' in dir)
        elif "y" in dir and obj.movement.direction.y:
            return abs(obj.movement.direction.y) > abs(obj.movement.direction.x) and (obj.movement.direction.y<0) == ('-' in dir)

    def update(self, pushable=False):
        if not self.direction and not pushable: return
        
        # Movement vector
        sprite = self.sprite
        self.collisions = {'L':[],'R':[],'T':[],'B':[],'all':[]}
        movement = self.direction * sprite.world.dt

        # Collision X
        sprite.hitbox.x += movement.x
        for obj in sprite.world.collides:
            if obj == sprite: continue
            if self.collide_with and not self.collide_with(obj): continue

            if sprite.hitbox.colliderect(obj.hitbox):
                if movement.x>0 or (pushable and self.obj_is_pushing(obj,'x-')):
                    self.collisions['R'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.right = obj.hitbox.left
                elif movement.x<0 or (pushable and self.obj_is_pushing(obj,'x+')):
                    self.collisions['L'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.left = obj.hitbox.right

        # Collision Y
        sprite.hitbox.y += movement.y
        for obj in sprite.world.collides:
            if obj == sprite: continue
            if self.collide_with and not self.collide_with(obj): continue
            
            if sprite.hitbox.colliderect(obj.hitbox):
                if   movement.y>0 or (pushable and self.obj_is_pushing(obj,'y-')):
                    self.collisions['B'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.bottom = obj.hitbox.top
                elif movement.y<0 or (pushable and self.obj_is_pushing(obj,'y+')):
                    self.collisions['T'].append(obj)
                    self.collisions['all'].append(obj)
                    sprite.hitbox.top = obj.hitbox.bottom

        # Update rect
        sprite.set_position(sprite.hitbox.center)
        