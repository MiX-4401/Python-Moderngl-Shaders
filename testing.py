"""
Author: Ethan.R
Date of Creation: 31st Febuary
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame   as pg
import numpy    as np

from _shaderPasses.bloom              import Bloom
from _shaderPasses.gaussianBlur       import GaussianBlur
from _shaderPasses.colourQuantise     import ColourQuantise
from _shaderPasses.dithering          import Dithering
from _shaderPasses.sobelFilter        import SobelFilter
from _shaderPasses.contrast           import Contrast
from _shaderPasses.greyScale          import GreyScale
from _shaderPasses.cannyEdgeDetection import CannyEdgeDetection

class ShaderProgram(Main):
    frag: str = """
        # version 460 core

        uniform sampler2D uTexture;
        //uniform float uTime;
        //uniform vec2 uResolution;

        in vec2 uvs;
        out vec4 fColour;
        
        //float wave = cos((colour.x - uTime * 0.01) * 6.283185307 * 5) * 0.5 + 0.5;

        const vec3 cColour1 = vec3(247.0/225.0, 0.0/225.0, 0.0/225.0);
        const vec3 cColour2 = vec3(199.0/225.0, 63.0/225.0, 10.0/225.0);
        const vec3 cColour3 = vec3(122.0/225.0, 8.0/225.0,  8.0/225.0);
        const vec3 cColour4 = vec3(3.0/225.0, 0.0/225.0, 0.0/225.0);
        
        //const vec3 cColour1 = vec3(81.0/225.0, 179.0/225.0, 214.0/225.0);
        //const vec3 cColour2 = vec3(70.0/225.0, 126.0/225.0, 214.0/225.0);
        //const vec3 cColour3 = vec3(50.0/225.0, 82.0/225.0,  209.0/225.0);
        //const vec3 cColour4 = vec3(29.0/225.0, 48.0/225.0,  122.0/225.0);

        void main(){

            // Sample texture
            vec3 baseColour = texture(uTexture, vec2(uvs.x * 0.2, uvs.y)).rgb;

            // Map frag to colour
            vec3 noise  = floor(baseColour * 10.0) / 5.0;
            vec3 bright = mix(cColour1, cColour2, noise);
            vec3 dark   = mix(cColour3, cColour4, noise);
            vec3 colour = mix(bright, dark, noise);
            //vec3 colour = mix(vec3(0.75, 0.0, 0.0), vec3(0.0, 0.0, 0.0), noise);

            fColour = vec4(colour, 1.0);
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
        #self.programs["new"]["uTime"] = self.time
        #self.programs["new"]["uResolution"] = self.textures["main"].size
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
        scale=3.0,
        flip=False,
        components=4,
        media=r"_images\NoiseCellular.png",
        fps=60
    ).run()