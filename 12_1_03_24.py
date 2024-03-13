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
        uniform float uTime;

        in vec2 uvs;
        out vec4 fColour;

        void main(){

            //vec4 scolour = texture(uTexture, uvs).rgba;
            vec2 sampleaa = vec2(sin(uvs.y * 10.0 + uTime * 0.04) * 0.002, cos(uvs.x * 10.0 + uTime * 0.04) * 0.002);
            vec4 scolour = texture(uTexture, uvs + sampleaa).rgba;

            if (uvs.y < 0.2){
                sampleaa = vec2(sin(uvs.y * 10.0 + uTime * 0.04) * 0.006, cos(uvs.x * 10.0 + uTime * 0.04) * 0.006);
                scolour = texture(uTexture, uvs + sampleaa).rgba;
            }
            
            
            float a = uTime;
            vec3 colour = vec3(0.0);


            if (scolour.r > 0.1){
                //fColour = vec4(mix(colour.r, sin(uTime * 0.04) * uvs.y, 0.2), mix(colour.g, uvs.x, 0.2), colour.b, colour.a);
                //fColour = vec4(colour.r, colour.gb, colour.a);
                
                // Fire effect
                colour.r = scolour.r + 1.0 - pow(uvs.y, 0.3);
                colour.g = scolour.g;
                colour.b = scolour.b;

            } else {
                fColour = vec4(0.0, 0.0, 0.0, 1.0);
            }

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

        self.create_texture(title="final", size=self.content.size, components=self.components)
        self.create_framebuffer(title="final", attachments=self.textures["final"])

    def update(self):
        # Update content shenanigans
        self.programs["new"]["uTime"] = self.time
        super().update()

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
        scale=0.5,
        flip=False,
        components=3,
        media=r"https://i.pinimg.com/originals/1c/ea/89/1cea8921ec29ef5ad81e7d55b2f3adba.jpg",
        fps=30,
    ).run()