"""
Author: Ethan.R
Date of Creation: 31st January 2024
Date of Release: NA
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame

import cv2
from PIL import Image

from _shaderPasses.bloom          import Bloom
from _shaderPasses.gaussianBlur   import GaussianBlur
from _shaderPasses.colourQuantise import ColourQuantise
from _shaderPasses.dithering      import Dithering
from _shaderPasses.sobelFilter    import SobelFilter
from _shaderPasses.contrast       import Contrast

class ShaderProgram(Main):
    program_frag: str = """
# version 460 core

uniform sampler2D myTexture;


in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 colour = texture(myTexture, uvs).rgba;

    fColour = vec4(colour.rgb, colour.a);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, fps:int=60, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)
        self.fps = 30

        self.load_program()

        # Load render target texture
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.start_texture.size, components=4)
        self.new_texture.filter: tuple    = (mgl.NEAREST, mgl.NEAREST)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Create shader program
        self.my_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.my_vao:     mgl.VertexArray = self.ctx.vertex_array(self.my_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])
        self.cap = cv2.VideoCapture(r"C:\Users\ejrad\OneDrive\Captures\Captures\Halo Infinite 2022-07-24 12-09-42.mp4")
    
    def garbage_cleanup(self):
        super().garbage_cleanup() # A better way then using decorators in this context
        self.my_program.release()
        self.my_vao.release()
        self.framebuffer.release()
        self.new_texture.release()

    @Main.d_update
    def update(self):
        
        succes, frame = self.cap.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, self.start_texture.size)
        image = Image.fromarray(frame_rgb)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        self.start_texture.write(image.tobytes())



    @Main.d_draw
    def draw(self):

        # Clear screen
        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()

        SobelFilter(ctx=self.ctx, size=self.new_texture.size, components=self.new_texture.components).run(
            texture=self.start_texture,
            output=self.framebuffer,
            threshold=0.005,
            blur_strength=(1,2,2)
        )

        # Render final_texture to screen
        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0

if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        caption="NA",
        swizzle="RGBA",
        scale=0.75,
        flip=False,
        components=3,
        path=r"_images\Untitled.png",
        fps=30,
    ).run()