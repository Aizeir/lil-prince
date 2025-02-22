from util import *
import array

from world import World

class Game:
    def __init__(self):
        # Window
        self.screen = pg.display.set_mode((W,H), pg.OPENGL | pg.DOUBLEBUF)
        pg.display.set_caption("The lil prince")
        pg.mouse.set_visible(0)
        self.clock = pg.time.Clock()
        self.fps = 60

        # Shaders
        self.load_shaders()

        # Fonts
        self.font = font("font.ttf", 40)

        # Scenes
        self.world = World(self)
        self.set_scene(self.world)
        
    def load_shaders(self):
        self.ctx = moderngl.create_context()
        self.vert_buffer = self.ctx.buffer(data=array.array('f', [
            # vertices (center) + texture uv coords (topleft comme pygame)
            -1.0, 1.0, 0.0, 0.0,  # topleft
            1.0, 1.0, 1.0, 0.0,  # topright
            -1.0, -1.0, 0.0, 1.0,  # bottomleft
            1.0, -1.0, 1.0, 1.0,  # bottomright
        ]))
        default_vert = load_shader("default.vert")
        world_frag = load_shader("default.frag")
        self.world_shader = self.ctx.program(vertex_shader=default_vert, fragment_shader=world_frag)
        self.world_render = self.ctx.vertex_array(self.world_shader, [(self.vert_buffer, '2f 2f', 'vert', 'texcoord')])

    def set_scene(self, scene):
        self.scene = scene
        self.scene.open()
        while True: self.update(scene)

    def update(self, scene):
        pg.display.flip()
        self.dt = self.clock.tick(self.fps) / 1000

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()
            scene.event(e)
        
        scene.update()
        scene.draw()

        # Render
        render(self.screen, self.scene.render, resolution=(W,H), time=pg.time.get_ticks())

Game()