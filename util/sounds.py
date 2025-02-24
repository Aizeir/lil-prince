import pygame as pg

def music(path, loops=-1, volume=1, fade_ms=1000):
    pg.mixer.music.load("assets/sounds/music/"+path)
    pg.mixer.music.set_volume(volume)
    pg.mixer.music.play(loops, 0, fade_ms)

sounds = {}
def sound(path, vol=.5):
    s = pg.mixer.Sound("assets/sounds/"+path)
    s.set_volume(vol)
    sounds[path.split('.')[0]] = s
    return s

select = sound("select.wav",.4)
jump = sound("jump.wav")
switch_planet = sound("switch_planet.wav", .2)
land = sound("land.wav")
hit = sound("hit.wav")
die = sound("die.wav")
plr_hit = sound("plr_hit.wav")
plr_die = sound("plr_die.wav")
shoot = sound("shoot.wav")
boom = sound("boom.wav")
powerup = sound("powerup.wav",.2)
powerup_2 = sound("powerup_2.wav",.2)
explosion = sound("explosion.wav",.4)
done = sound("done.wav",.3)
rocket = sound("rocket.wav",.3)
heal = sound("heal.wav",.4)
life = sound("life.wav",.7)
