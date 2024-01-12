"""
Author: Ethan.R
Date: 13th November 2023
"""

import pygame, moderngl, numpy
from sys import exit
import requests
from PIL import Image
from io import BytesIO

class Main():
    main_vertex: str = """
# version 460 core

in vec2 aPosition;
in vec2 aTexCoord;
out vec2 uvs;

void main(){

    uvs = aTexCoord;

    gl_Position = vec4(aPosition, 0.0, 1.0);
}
"""
    main_frag:   str = """
# version 460 core

uniform sampler2D myTexture;
in vec2 uvs;
out vec4 fColour;

void main(){

    vec4 colour = texture(myTexture, uvs).rgba; 

    fColour = vec4(colour.rgb, colour.a);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None", headless:bool=False):
        self.headless:   bool = headless
        self.caption:    str  = caption
        self.url:        str  = url
        self.path:       str  = path
        self.scale:      int  = scale
        self.swizzle:    str  = swizzle
        self.components: int  = components
        self.method:     int  = method
        self.time:       int  = 0
        self.flip:       bool = flip

    def load_program(self):

        if self.url != "None":
            self.image_data: Image.Image = self.get_image_from_url(scale=self.scale, url=self.url, flip=self.flip) 
        elif self.path != "None":
            self.image_data = self.get_image_from_file(scale=self.scale, path=self.path, flip=self.flip)


        # Pygame Boilerplate
        self.clock:  pygame.time.Clock = pygame.time.Clock()
        if self.headless:
            self.screen: pygame.Surface    = pygame.display.set_mode(self.image_data.size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.NOFRAME)
        else: self.screen: pygame.Surface    = pygame.display.set_mode(self.image_data.size, pygame.DOUBLEBUF | pygame.OPENGL)
        self.fps: int = 60
        pygame.display.set_caption(self.caption)

        # Moderngl Boilerplate
        self.ctx: moderngl.Context = moderngl.create_context()
        self.main_program: moderngl.Program = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=Main.main_frag)
        self.quad_buffer:  moderngl.Buffer  = self.ctx.buffer(data=numpy.array([-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype="f4"))
        self.main_vao: moderngl.VertexArray = self.ctx.vertex_array(self.main_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])
        self.ctx.enable(moderngl.BLEND)
        
        self.my_texture: moderngl.Texture = self.get_texture_from_data(image_data=self.image_data)
        self.my_texture.swizzle: str = self.swizzle
        
    def get_image_from_url(self, url:str, scale:int, flip:bool):
        response: requests.Response = requests.get(url)
        image_data: Image.Image = Image.open(BytesIO(response.content))
        image_data = image_data.transpose(Image.FLIP_TOP_BOTTOM) if flip == True else image_data
        image_data = image_data.resize(size=(round((image_data.size[0] * scale)), round(image_data.size[1] * scale)), resample=Image.NEAREST)
        
        return image_data

    def get_image_from_file(self, path:str, scale:int, flip:bool):
        image_data: Image.Image = Image.open(path)
        image_data = image_data.transpose(Image.FLIP_TOP_BOTTOM) if flip == True else image_data
        image_data = image_data.resize(size=(round((image_data.size[0] * scale)), round(image_data.size[1] * scale)), resample=Image.NEAREST)
        
        return image_data

    def get_texture_from_data(self, image_data:Image.Image):
        
        my_texture: moderngl.Texture = self.ctx.texture(size=image_data.size, components=self.components, data=image_data.tobytes())
        if self.method == "nearest":
            my_texture.filter: tuple = (moderngl.NEAREST, moderngl.NEAREST)
        elif self.method == "linear":
            my_texture.filter: tuple = (moderngl.LINEAR, moderngl.LINEAR)
        else:
            raise f"Invalid scaling method {self.method} and not ['nearest', 'linear]"
        return my_texture
    

    def garbage_cleanup(self):
        self.ctx.release()
        self.main_program.release()
        self.quad_buffer.release()
        self.main_vao.release()
        self.my_texture.release()

    @classmethod
    def d_garbage_cleanup(cls, func):
        def inner(self, *args, **kwargs):

            self.ctx.release()
            self.main_program.release()
            self.quad_buffer.release()
            self.main_vao.release()
            self.my_texture.release()

            result = func(self, *args, **kwargs)
            return result
        
        return inner

    def update_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.garbage_cleanup()
                pygame.quit()
                exit()

    @classmethod
    def d_update(cls, func):
        def inner(self, *args, **kwargs):

            self.time += 1

            pygame.display.set_caption(f"{self.caption} | FPS: {round(self.clock.get_fps())} | TIME: {self.time}")

            result = func(self, *args, **kwargs)
            return result
        
        return inner

    def update(self):
        self.time += 1
        pygame.display.set_caption(f"{self.caption} | FPS: {round(self.clock.get_fps())} | TIME: {self.time}")

    @classmethod
    def d_draw(cls, func):
        def inner(self, *args, **kwargs):

            result = func(self, *args, **kwargs)

            self.ctx.screen.use()
            self.ctx.clear(0.0, 0.0, 0.0)
            self.main_vao.render(mode=moderngl.TRIANGLE_STRIP)
            pygame.display.flip()

            return result
        
        return inner

    def draw(self):

        self.ctx.screen.use()
        self.ctx.clear(0.0, 0.0, 0.0)
        self.main_vao.render(mode=moderngl.TRIANGLE_STRIP)
        pygame.display.flip()

    def run(self):

        while True:
            self.update_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)


