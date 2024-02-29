
import pygame as pg
import moderngl as mgl
import numpy as np
import requests as req
import cv2
from PIL import Image
from io import BytesIO
from sys import exit

class ShaderProgram():
    vert: str = """
        # version 460 core

        in vec2 bPosition;
        in vec2 bTexCoord;
        out vec2 uvs;

        void main(){

            uvs = aTexCoord;

            gl_Position = vec4(bPosition, 0.0, 1.0);
        }
    """

    frag: str = """
        # version 460 core

        uniform sampler2D myTexture;
        in vec2 uvs;
        out vec4 fColour;

        void main(){

            vec4 colour = texture(myTexture, uvs).rgba; 

            fColour = vec4(colour.rgb, colour.a);
        }
    """

    def __init__(self, media:str, scale:int, caption:str="NA", swizzle:str="RGBA", flip:bool=False, components:int=4, method:str="nearest", fps:int=60):
        self.path:    str = media
        self.caption: str = caption
        self.swizzle: str = swizzle
        self.scale:   int = scale
        self.fps:     int = fps
        self.flip:   bool = flip
        self.method:  str = method

        self.framebuffers: dict = {}
        self.textures:      dict = {}
        self.programs:     dict = {}
        self.vaos:         dict = {}
        self.buffers:      dict = {}

        self.content: Image.Image = None

    def load_program(self):
        self.load_media()
        self.load_pygame()
        self.load_moderngl()

        
    def load_media(self):
        # Get media content

        if self.media.split(".")[-1] in ["png", "jpg", "jpeg"]:
            # Load local image file
            content: Image.Image = Image.open(fp=self.media)

        elif self.media.split(".")[-1] in ["mp4"]:
            # Load local video file
            capture: cv2.VideoCapture = cv2.VideoCapture(self.load_media)
            success, frame = capture.read()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            content: Image.Image = Image.fromarray(frame_rgb)
            
        else:
            # Load cloud image file
            response: req.Response = req.get(self.media)
            content: Image.Image   = Image.open(BytesIO(response.contect))

        # Transform content image
        content = content.transpose(Image.FLIP_TOP_BOTTOM) if self.flip == True else content
        content = content.resize(size=(round((content.size[0] * self.scale)), round(content.size[1] * self.scale)), resample=Image.NEAREST)

        self.content = content

    def load_pygame(self):
        # Pygame Boilerplate
        self.clock: pg.time.Clock = pg.time.Clock()
        self.screen: pg.Surface = pg.display.set_mode((), pg.DOUBLEBUF | pg.OPENGL)
        pg.display.set_caption(title=self.caption)

    def load_moderngl(self):
        # Moderngl Boilerplate
        self.ctx: mgl.Context = mgl.create_context()
        self.create_program(title="main", vert=ShaderProgram.vert, frag=ShaderProgram.frag)
        self.create_buffer(title="main", data=np.array([-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype="f4"))
        self.create_vao(title="main", program="main", args=["2f 2f", "bPosition", "bTexCoord"])
        self.ctx.enable(mgl.BLEND)

    def create_framebuffer(self, title:str, attachments:list=[]):
        self.framebuffers[title]: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=attachments)
    
    def create_texture(self, title:str, size:tuple, components:int=4):
        self.textures[title]: mgl.Texture = self.ctx.texture(size=size, components=components)
    
    def create_program(self, title:str, vert:str, frag:str):
        self.programs[title]: mgl.Program = self.ctx.program(vertex_shader=vert, fragment_shader=frag)
    
    def create_vaos(self, title:str, program:str, buffer:str, args:list=[]):
        self.vaos[title]: mgl.VertexArray = self.ctx.vertex_array(program=self.programs[program], [(self.buffers[buffer], *args)])
   
    def create_buffer(self, title:str, data:np.array):
        self.buffers[title]: mgl.Buffers = self.ctx.buffer(data=data)


    def garbage_cleanup(self):
        for program in self.programs:
            self.programs[program].release()
        for vao in self.vaos:
            self.vaos[vao].release()
        for buffer in self.buffers:
            self.buffers[buffer].release()
        for texture in self.textures:
            self.textures[texture].release()
        for framebuffer in self.framebuffers:
            self.framebuffers[framebuffer].release()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.garbage_cleanup()
                pg.quit()
                exit()

    def update(self):
        pass

    def draw(self):
        pass

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
