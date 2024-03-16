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
from PIL import Image
from queue import LifoQueue
import numpy as np
import cv2

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
        self.create_texture(title="new", size=self.textures["main"].size, components=self.textures["main"].components)
        self.create_framebuffer(title="new", attachments=self.textures["new"])
        self.add_shaderpass(title="sobel", shader=SobelFilter)
        
        self.media_type = "image"

        self.raw_frames: LifoQueue = LifoQueue()
        self.new_frames: LifoQueue = LifoQueue()
        
        self.thread_1:    thr.Thread = thr.Thread(target=self.get_frames,     daemon=True)
        self.thread_2:    thr.Thread = thr.Thread(target=self.convert_frames, daemon=True)
        self.thread_1.start()
        self.thread_2.start()

    def get_frames(self):
        
        success: bool; content: None
        capture = cv2.VideoCapture(self.media)
        success, content = capture.read()
        content = cv2.cvtColor(content, cv2.COLOR_BGR2RGB)
        self.raw_frames.put(content)

        while success:
            success, content = capture.read()
            content = cv2.cvtColor(content, cv2.COLOR_BGR2RGB)
            self.raw_frames.put(content)

    def convert_frames(self):

        while True:
            if self.new_frames.qsize() >= self.frame_count:
                break
            
            content = self.raw_frames.get()
            content = cv2.resize(content, self.textures["main"].size)
            content = cv2.flip(src=content, flipCode=0) if self.flip else content
            self.new_frames.put(content)
            
    def update(self):
        # Update content shenanigans
        self.textures["main"].write(np.array(object=self.new_frames.get()).tobytes())
        super().update()

    def draw(self):

        # Draw content shenanigans

        self.shader_passes["sobel"].run(
            texture=self.textures["main"],
            output=self.framebuffers["new"],
            threshold=0.1
        )

        # self.framebuffers["new"].use()
        # self.textures["main"].use(location=0)
        # self.programs["new"]["uTexture"] = 0
        # self.vaos["new"].render(mgl.TRIANGLE_STRIP)

        self.textures["new"].use(location=0)
        self.programs["main"]["uTexture"] = 0
        super().draw()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()

if __name__ == "__main__":
    ShaderProgram(
        caption="Sobel Filter Video w\ Multithreading",
        swizzle="RGBA",
        scale=0.75,
        flip=True,
        components=3,
        media=r"_images\video_2.mp4",
        fps=60,
    ).run()