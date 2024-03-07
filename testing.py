"""
Author: Ethan.R
Date of Creation: 31st January 2024
Date of Release: NA
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame as pg
import threading as thr

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

            fColour = vec4(colour.rgb, colour.a);
    }
"""

    def __init__(self, media:str, scale:int=1, caption:str="NA", swizzle:str="RGBA", flip:bool=False, components:int=4, method:str="nearest", fps:int=60):
        super().__init__(media=media, scale=scale, caption=caption, swizzle=swizzle, flip=flip, components=components, method=method, fps=fps)
        
        # Shader Shenanigans
        self.load_program()

        self.create_program(title="new", vert=Main.vert, frag=ShaderProgram.frag)
        self.create_vao(title="new", program="new", buffer="main", args=["2f 2f", "iPosition", "iTexCoord"])
        self.create_texture(title="front", size=self.textures["main"].size, components=self.textures["main"].components)
        self.create_framebuffer(title="front", attachments=self.textures["front"])

        self.create_texture(title="back", size=self.textures["main"].size, components=self.components)
        self.create_framebuffer(title="back", attachments=[self.textures["back"]])

        self.add_shaderpass(title="Sobelfilter", shader=SobelFilter)

        self.media_type = "image"

        self.threads: list = []
        thr.Thread(target=self.get_frames())

    def get_frames(self):
        while True:
            success, frame = self.next_frame()

    def update(self):
        # Update content shenanigans
        super().update()
        pass
        
    def draw(self):
        
        self.shader_passes["Sobelfilter"].run(
            texture=self.textures["main"],
            output=self.framebuffers["front"],
            threshold=0.1
        )

        # Draw content shenanigans
        # self.framebuffers["front"].use()
        # self.textures["main"].use(location=0)
        # self.programs["new"]["uTexture"] = 0
        # self.vaos["new"].render(mgl.TRIANGLE_STRIP)

        self.textures["front"].use(location=0)
        self.programs["main"]["uTexture"] = 0
        super().draw()
        

if __name__ == "__main__":
    ShaderProgram(
        caption="I'm Testing Here!",
        swizzle="RGBA",
        scale=0.75,
        flip=True,
        components=3,
        media=r"C:\Users\ejrad\OneDrive\Captures\Captures\Starfield 2023-09-06 19-09-23.mp4",
        fps=60,
    ).run()