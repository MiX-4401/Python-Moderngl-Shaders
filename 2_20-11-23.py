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
        uniform float time;
        uniform vec2 resolution;
        in vec2 uvs;
        out vec4 fColour;

        float get_vig(vec2 pos){
            float distance = length(pos);

            float radius   = 0.6;
            float softness = 0.1;
            float vigIntensity = smoothstep(radius, radius - softness, 1 - distance);

            return vigIntensity;
        }

        vec4 get_sepia(vec4 colour){
            float intensity = 0.1;
            
            float r = colour.r;
            float g = colour.g;
            float b = colour.b;
            
            colour.r = (r * (1.0 - 2.0 * intensity) + g * (0.769 + 0.231 * intensity) + b * (0.189 + 0.711 * intensity));
            colour.g = (r * 0.349 + g * (1.0 - intensity) + b * 0.168);
            colour.b = (r * 0.272 + g * 0.534 + b * (1.0 - intensity));

            colour = clamp(colour, 0.0, 1.0);

            return colour;
        }

        float get_noise(vec2 pos){
            return fract(sin(dot(pos.xy, vec2(12.9898,78.233))) * 43758.5453);
        }

        void main(){

            vec2 pos = vec2(gl_FragCoord.xy / resolution) - 0.5;
            
            float vigIntensity = get_vig(pos);
            float noise_value = get_noise(uvs * time);

            vec4 colour      = texture(uTexture, uvs).rbga;
            vec4 finalColour = get_sepia(colour) - 0.09;
            //vec4 finalColour = colour;
            finalColour.rgb  = mix(finalColour.rgb, finalColour.rgb + vec3(noise_value), 0.19);

            fColour = vec4(finalColour.rgb, finalColour.a) * (1 - vigIntensity);
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
        self.programs["new"]["time"] = self.time
        self.programs["new"]["resolution"] = self.screen.get_size()
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
        media=r"https://pre00.deviantart.net/949a/th/pre/i/2013/044/0/d/the_kookaburra_by_kqeina-d5us1tb.png",
        caption="20/11/23",
        swizzle="RBGA",
        components=4,
        scale=1,
        flip=True
    ).run()