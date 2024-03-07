"""
Author: Ethan.R
Date of Creation: 31st January 2024
Date of Release: NA
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame as pg
import pyautogui as pya
import cv2
import numpy as np
from PIL import Image

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
        uniform float uTime;

        in vec2 uvs;
        out vec4 fColour;

        vec3 scolour = vec3(0.0);

        void main(){
            vec4 colour = texture(uTexture, uvs).rgba;

            if (colour.r > 0.5){
                scolour.r = 0.0;
                scolour.b = colour.g;
                scolour.g = 0.0;
            }
            else if (colour.r < 0.5){
                scolour.r = colour.r;
                scolour.g = colour.g;
                scolour.b = colour.b;
            }
            else {
                scolour.r = 0.0;
                scolour.g = 0.0;
                scolour.b = 0.0;
            }

            fColour = vec4(scolour, 1.0);
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

        self.create_texture(title="final", size=self.content.size, components=self.components)
        self.create_framebuffer(title="final", attachments=self.textures["final"])

    def update(self):

        self.time += 1
        pg.display.set_caption(f"{self.caption} | FPS: {round(self.clock.get_fps())} | TIME: {self.time}")

    def next_frame(self):
        
        # Read frame
        content = pya.screenshot()
        frame_rgb = cv2.cvtColor(np.array(content), cv2.COLOR_BGR2RGB)
        content = Image.fromarray(frame_rgb)

        # Transform content image
        content = content.transpose(Image.FLIP_TOP_BOTTOM) if self.flip == True else content
        content = content.resize(size=(round((content.size[0] * self.scale)), round(content.size[1] * self.scale)), resample=Image.NEAREST)

        # Write content to moderngl texture
        self.textures["main"].write(content.tobytes())

    def draw(self):

        SobelFilter(ctx=self.ctx, size=self.textures["main"].size, components=self.components).run(
            texture=self.textures["main"],
            output=self.framebuffers["new"],
            threshold=0.1,
        )

        # Draw content shenanigans
        self.framebuffers["final"].use()
        # self.framebuffers["new"].use()
        # self.textures["main"].use(location=0)
        self.textures["new"].use(location=0)
        self.programs["new"]["uTexture"] = 0
        self.vaos["new"].render(mgl.TRIANGLE_STRIP)

        self.textures["final"].use(location=0)
        self.programs["main"]["uTexture"] = 0
        super().draw()
        

if __name__ == "__main__":
    ShaderProgram(
        caption="",
        swizzle="RGBA",
        scale=0.9,
        flip=False,
        components=3,
        media=r"C:\Users\ejrad\OneDrive\Captures\Apex\Apex Legends 2023-09-10 12-57-20.mp4",
        fps=30,
    ).run()