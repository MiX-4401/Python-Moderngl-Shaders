"""
Author: Ethan.R
Date of Creation: 31st January 2024
Date of Release: NA
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame as pg

from _shaderPasses.bloom          import Bloom
from _shaderPasses.gaussianBlur   import GaussianBlur
from _shaderPasses.colourQuantise import ColourQuantise
from _shaderPasses.dithering      import Dithering
from _shaderPasses.sobelFilter    import SobelFilter
from _shaderPasses.contrast       import Contrast

class ShaderProgram(Main):
    frag: str = """
        # version 460 core

        uniform sampler2D uTexture;

        in vec2 uvs;
        out vec4 fColour;

        void main(){
            vec4 colour = texture(uTexture, uvs).rgba;

            fColour = vec4(1.0 - colour.rgb, colour.a);
    }
"""

    def __init__(self, media:str, scale:int=1, caption:str="NA", swizzle:str="RGBA", flip:bool=False, components:int=4, method:str="nearest", fps:int=60):
        super().__init__(media=media, scale=scale, caption=caption, swizzle=swizzle, flip=flip, components=components, method=method, fps=fps)
        
        # Shader Shenanigans
        self.load_program()

        self.create_program(title="new", vert=Main.vert, frag=ShaderProgram.frag)
        self.create_vao(title="new", program="new", buffer="main", args=["2f 2f", "iPosition", "iTexCoord"])
        self.create_texture(title="new", size=self.textures["main"].size, components=self.textures["main"].components)
        self.create_framebuffer(title="new", attachments=self.textures["new"])


    def update(self):
        # Update content shenanigans

        super().update()

    def draw(self):

        # Draw content shenanigans
        self.framebuffers["new"].use()
        self.textures["main"].use(location=0)
        self.programs["new"]["uTexture"] = 0
        self.vaos["new"].render(mgl.TRIANGLE_STRIP)

        self.textures["new"].use(location=0)
        self.programs["main"]["uTexture"] = 0
        super().draw()
        

if __name__ == "__main__":
    ShaderProgram(
        caption="I'm Testing Here!",
        swizzle="RGBA",
        scale=1.0,
        flip=False,
        components=4,
        media=r"_images\0TextureWall.png",
        fps=30,
    ).run()