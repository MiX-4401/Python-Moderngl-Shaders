"""
Author: Ethan.R
Date of Creation: 31st Febuary
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame   as pg
import numpy    as np

from _shaderPasses.bloom          import Bloom
from _shaderPasses.gaussianBlur   import GaussianBlur
from _shaderPasses.colourQuantise import ColourQuantise
from _shaderPasses.dithering      import Dithering
from _shaderPasses.sobelFilter    import SobelFilter
from _shaderPasses.contrast       import Contrast
from _shaderPasses.greyScale      import GreyScale

class ShaderProgram(Main):
    frag: str = """
        # version 460 core

        uniform sampler2D uTexture1;
        uniform sampler2D uTexture2;

        in vec2 uvs;
        out vec4 fColour;

        void main(){
            vec3 colour1 = texture(uTexture1, uvs).rgb;
            vec3 colour2 = texture(uTexture2, uvs).rgb;

            float luminence = dot(colour1 - colour2, vec3(0.2126, 0.7152, 0.0722));

            if (luminence < 0.01){
                fColour = vec4(0.0, 0.0, 0.0, 1.0);
            } else {
                fColour = vec4(1.0, 1.0, 1.0, 1.0);
            }          
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

        self.create_texture(title="grey", size=self.textures["main"].size, components=self.textures["main"].components)
        self.create_framebuffer(title="grey", attachments=self.textures["grey"])
        self.create_texture(title="g1", size=self.textures["main"].size, components=self.textures["main"].components)
        self.create_framebuffer(title="g1", attachments=self.textures["g1"])
        self.create_texture(title="g2", size=self.textures["main"].size, components=self.textures["main"].components)
        self.create_framebuffer(title="g2", attachments=self.textures["g2"])
        
        self.add_shaderpass(title="blur", shader=GaussianBlur)
        self.add_shaderpass(title="greyscale", shader=GreyScale)

    def update(self):
        # Update content shenanigans

        super().update()

    def draw(self):
        self.shader_passes["greyscale"].run(
            texture=self.textures["main"],
            output=self.framebuffers["grey"]
        )

        self.shader_passes["blur"].run(
            texture=self.textures["main"],
            output=self.framebuffers["g1"],
            x=1
        )
        self.shader_passes["blur"].run(
            texture=self.textures["main"],
            output=self.framebuffers["g2"],
            x=4
        )
        

        # Draw content shenanigans
        self.framebuffers["new"].use()
        self.textures["g1"].use(location=0)
        self.textures["g2"].use(location=1)
        self.programs["new"]["uTexture1"] = 0
        self.programs["new"]["uTexture2"] = 1
        self.vaos["new"].render(mgl.TRIANGLE_STRIP)

        self.textures["new"].use(location=0)
        self.programs["main"]["uTexture"] = 0
        super().draw()
        

if __name__ == "__main__":
    ShaderProgram(
        caption="I'm Testing Here!",
        swizzle="RGBA",
        scale=0.75,
        flip=True,
        components=3,
        # media=r"_images\4TextureOutback.jpg",
        media=r"_images\video_2.mp4",
        fps=60,
    ).run()