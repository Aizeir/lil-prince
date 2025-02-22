import pygame as pg, moderngl
import os, time, sys, json
from random import randint, shuffle, choice
pg.mixer.pre_init(44100, 16, 2, 4096)
pg.init()

import util.sounds as sounds
from util.keybinds import *
from util.settings import *
from util.timer import *

# Debug
debug_font = pg.font.Font(None,30)
def debug(info, y=16, x=16, font=debug_font):
    surf = pg.display.get_surface()
    debug_surf = font.render(str(info),1,WHITE)
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    pg.draw.rect(surf, BLACK, debug_rect.inflate(4, -6))
    surf.blit(debug_surf, debug_rect)

def screenshot(display, name=None):
    pg.image.save(display, name or f"capture{pg.time.get_ticks()}.png")

t = 0
def print_time(text):
    global t
    t2 = pg.time.get_ticks()
    if text:
        print(text, t2-t)
    t = t2

# Text
def font(path, size):
    return pg.font.Font("assets/ui/"+path, size)
def textr(text, font, color, **k):
    t = font.render(str(text), False, color)
    return t, t.get_rect(**k)
# Util
def iskeys(keys, K):
    return any([keys[k] for k in K])
def proba(x):
    return randint(1,x)==1
def clamp(m, x, M=None):
    if M != None: return max(m,min(x,M))
    else: return min(m, x)
def normalize(vec):
    vec = vec2(vec)
    return vec.normalize() if vec!=vec2() else vec2()
def filebase(filename):
    return os.path.basename(filename).split(".")[0]
def get_rect(image, pos, origin=TOPLEFT):
    return image.get_rect(topleft=pos) if origin==TOPLEFT else image.get_rect(center=pos)
def get_hitbox(rect, hitbox):
    if hitbox is None: return rect
    return pg.Rect([i*SCALE for i in hitbox]).move(rect.topleft)

# Mask
def to_mask(img, color=UI['white'], bg=(0,0,0,0)):
    return pg.mask.from_surface(img).to_surface(setcolor=color, unsetcolor=bg)

# Image
def load_img(image):
    return pg.image.load(image).convert_alpha()

def load(image, scale=1):
    if isinstance(image, str):
        image = load_img("assets/"+image+".png")
    if scale != 1:
        image = pg.transform.scale_by(image, scale)
    return image

def flips(images, x=1, y=0):
    return [pg.transform.flip(img,x,y) for img in images]

def load_folder(path, scale=SCALE):
    images = []
    for _, _, files in os.walk("assets/"+path):
        for filename in files:
            images.append(load(f"{path}/{filename.split(".")[0]}", scale))
    return images

def load_folder_dict(path, scale=SCALE):
    image_dict = {}
    for _, _, files in os.walk("assets/"+path):
        for filename in files:
            name = filename.split(".")[0]
            image_dict[name] = load(f"{path}/{name}", scale)
    return image_dict

def load_tileset(path, size=(16,16), scale=SCALE):
    image = load(path, scale)
    size = (size[0]*scale,size[1]*scale)
    tilemap = []
    
    for y in range(image.get_height()//size[1]):
        for x in range(image.get_width()//size[0]):
            tilemap.append(image.subsurface((x*size[0], y*size[1], size[0], size[1])))
    return tilemap

# Outline
def outline(img):
    surf = pg.Surface((img.get_width()+2*SCALE,img.get_height()+SCALE),pg.SRCALPHA,32).convert_alpha()
    border = pg.mask.from_surface(img).to_surface(unsetcolor=(0,0,0,0),setcolor="white")
    for dx,dy in ((-SCALE,0),(SCALE,0),(0,-SCALE)):
        surf.blit(border, (SCALE+dx,SCALE+dy))
    return surf
    
# Animate
def frame_time(time, anim_speed, length=None):
    frame_idx = (pg.time.get_ticks()-time) // (1000//anim_speed)
    return frame_idx % length if length!=None else frame_idx

# Sides
def sides(action, anim, with_outline=False):
    if isinstance(anim, pg.Surface): anim = [anim]
    f = flips(anim)
    if with_outline:
        return {action+'_L': [(i,outline(i)) for i in f], action+'_R': [(i,outline(i)) for i in anim]}
    else:
        return {action+'_L': f, action+'_R': anim}

def sides4(action, T,B,R=None,L=None):
    return {
        action+'_T': T,
        action+'_B': B,
        action+'_R': R or flips(L),
        action+'_L': L or flips(R),
    }

# Shaders
def load_shader(name):
    with open(f"assets/shaders/{name}", 'r') as file:
        return file.read()

def texture(ctx, surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

def render(tex, render, **uniforms):
    if isinstance(tex, pg.Surface):
        tex = texture(render.ctx, tex)
    textures = [tex]
    tex.use(0)
    for uniform, value in uniforms.items():
        if isinstance(value, pg.Surface):
            value = texture(render.ctx, value)
        if isinstance(value, moderngl.Texture):
            value.use(len(textures))
            render.program[uniform] = len(textures)
            textures.append(value)
        else:
            try:
                render.program[uniform] = value
            except: pass
    render.render(mode=moderngl.TRIANGLE_STRIP)

    for i, t in enumerate(textures):
        t.release()