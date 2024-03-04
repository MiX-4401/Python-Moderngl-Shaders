
import pygame as pg
import moderngl as mgl
import numpy as np
import requests as req
import cv2
from PIL import Image
from io import BytesIO
from sys import exit

class Main():
    vert: str = """
        # version 460 core

        in vec2 iPosition;
        in vec2 iTexCoord;
        out vec2 uvs;

        void main(){

            uvs = iTexCoord;

            gl_Position = vec4(iPosition, 0.0, 1.0);
        }
    """

    frag: str = """
        # version 460 core

        uniform sampler2D uTexture;
        in vec2 uvs;
        out vec4 fColour;

        void main(){

            vec4 colour = texture(uTexture, uvs).rgba; 

            fColour = vec4(colour.rgb, colour.a);
        }
    """

    def __init__(self, media:str, scale:int=1, caption:str="NA", swizzle:str="RGBA", flip:bool=False, components:int=4, method:str="nearest", fps:int=60):
        self.media:   str = media
        self.caption: str = caption
        self.swizzle: str = swizzle
        self.scale:   int = scale
        self.fps:     int = fps
        self.flip:   bool = flip
        self.method:  str = method
        self.components: int = components

        self.framebuffers: dict = {}
        self.textures:     dict = {}
        self.programs:     dict = {}
        self.vaos:         dict = {}
        self.buffers:      dict = {}

        self.time: int = 0
        self.content: Image.Image = None
        self.media_type: str = None
        self.video_capture: cv2.VideoCapture = None

    def load_program(self):
        self.load_media()
        self.load_pygame()
        self.load_moderngl()

    def load_media(self):
        # Get media content

        self.media_type = "image"

        if self.media.split(".")[-1] in ["png", "jpg", "jpeg"] and "https" not in self.media:
            # Load local image file
            content: Image.Image = Image.open(fp=self.media)

        elif self.media.split(".")[-1] in ["mp4"]:
            # Load local video file
            capture: cv2.VideoCapture = cv2.VideoCapture(self.media)
            success, frame = capture.read()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            content: Image.Image = Image.fromarray(frame_rgb)

            self.media_type = "video"
            self.video_capture = capture
        else:
            # Load cloud image file
            response: req.Response = req.get(self.media)
            content: Image.Image   = Image.open(BytesIO(response.content))

        # Transform content image
        content = content.transpose(Image.FLIP_TOP_BOTTOM) if self.flip == True else content
        content = content.resize(size=(round((content.size[0] * self.scale)), round(content.size[1] * self.scale)), resample=Image.NEAREST)

        self.content = content

    def load_pygame(self):
        # Pygame Boilerplate
        self.clock: pg.time.Clock = pg.time.Clock()
        self.screen: pg.Surface = pg.display.set_mode(self.content.size, pg.DOUBLEBUF | pg.OPENGL)
        pg.display.set_caption(self.caption)

    def load_moderngl(self):
        # Moderngl Boilerplate
        self.ctx: mgl.Context = mgl.create_context()
        self.create_program(title="main", vert=Main.vert, frag=Main.frag)
        self.create_buffer(title="main", data=np.array([-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype="f4"))
        self.create_vao(title="main", program="main", buffer="main", args=["2f 2f", "iPosition", "iTexCoord"])
        self.ctx.enable(mgl.BLEND)

        # Create main texture/framebuffer
        self.create_texture(title="main", size=self.content.size, components=self.components, swizzle=self.swizzle, method=self.method)
        self.create_framebuffer(title="main", attachments=[self.textures["main"]])
        self.textures["main"].write(data=self.content.tobytes())

    def create_framebuffer(self, title:str, attachments:list=[]):
        self.framebuffers[title]: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=attachments)
    
    def create_texture(self, title:str, size:tuple, components:int=4, method:str="nearest", swizzle:str="RGBA"):
        self.textures[title]: mgl.Texture = self.ctx.texture(size=size, components=components)
        
        self.textures[title].swizzle: str = swizzle
        if method == "nearest":
            self.textures[title].filter: tuple = (mgl.NEAREST, mgl.NEAREST)  
        elif method == "linear":
            self.textures[title].filter: tuple = (mgl.LINEAR, mgl.LINEAR)

    def create_program(self, title:str, vert:str, frag:str):
        self.programs[title]: mgl.Program = self.ctx.program(vertex_shader=vert, fragment_shader=frag)
    
    def create_vao(self, title:str, program:str, buffer:str, args:list=[]):
        self.vaos[title]: mgl.VertexArray = self.ctx.vertex_array(self.programs[program], [(self.buffers[buffer], *args)])
        
    def create_buffer(self, title:str, data:np.array):
        self.buffers[title]: mgl.Buffers = self.ctx.buffer(data=data)


    def next_frame(self):

        # Read frame
        success, frame = self.video_capture.read()

        if success:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            content = Image.fromarray(frame_rgb)

            # Transform content image
            content = content.transpose(Image.FLIP_TOP_BOTTOM) if self.flip == True else content
            content = content.resize(size=(round((content.size[0] * self.scale)), round(content.size[1] * self.scale)), resample=Image.NEAREST) if self.scale != 1 else content
        else:
            content = Image.new("RGB", size=self.textures["main"].size, color=(0,0,0))

        new_texture: mgl.texture = self.ctx.texture(size=self.textures["main"].size, components=self.components)
        new_texture.write(content.tobytes())

        # Write content to moderngl texture
        self.textures["main"] = new_texture

        return success, new_texture

    def get_image_data_from_file(self, path:str, scale:int, flip:bool):
        content: Image.Image = Image.open(path)
        content = content.transpose(Image.FLIP_TOP_BOTTOM) if flip == True else content
        content = content.resize(size=(round((content.size[0] * scale)), round(content.size[1] * scale)), resample=Image.NEAREST)
        
        return content.tobytes()


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
        self.time += 1
        pg.display.set_caption(f"{self.caption} | FPS: {round(self.clock.get_fps())} | TIME: {self.time}")

    def draw(self):

        self.ctx.screen.use()
        self.ctx.screen.clear()
        self.vaos["main"].render(mode=mgl.TRIANGLE_STRIP)
        pg.display.flip()

        if self.media_type == "video":
            self.next_frame()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)










