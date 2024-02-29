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
        uniform sampler2D uNormal;
        uniform vec2 resolution;
        uniform vec3 fallOff;
        uniform vec3 lightPos;
        uniform vec3 lightColour;
        uniform vec3 ambientColour;
        uniform float ambientIntensity;

        in vec2 uvs;
        out vec4 fColour;

        void main(){
            vec4 tAlbedo = texture(uTexture, uvs).rgba;
            vec3 tNormal = texture(uNormal, uvs).rgb;

            vec3 lightDir = vec3(lightPos.xy - (gl_FragCoord.xy / resolution.xy), lightPos.z);
            lightDir.x *= resolution.x / resolution.y;
            float d     = length(lightDir);

            vec3 normal = normalize(tNormal * 2.0 - 1.0);
            vec3 light  = normalize(lightDir);

            vec3 diffuse = lightColour * max(dot(normal, light), 0.0);
            float attenuation = 1.0 / (fallOff.x + (fallOff.y * d) + (fallOff.z * d * d));
            vec3 finalColour = ambientColour * ambientIntensity + diffuse * attenuation;
            fColour = vec4(tAlbedo.rgb * finalColour, tAlbedo.a);
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

        self.create_texture(title="normal", size=self.textures["main"].size, components=self.textures["main"].components)
        self.textures["normal"].write(data=self.get_image_data_from_file(scale=24, flip=True, path=r"_images\2NormalPlayer.png"))

    def update(self):
        # Update content shenanigans
        mouse_x: int = round(pg.mouse.get_pos()[0], 2) / self.screen.get_size()[0]
        mouse_y: int = round(pg.mouse.get_pos()[1], 2) / self.screen.get_size()[1]
        self.programs["new"]["resolution"]    = self.screen.get_size()
        self.programs["new"]["fallOff"]       = (0.00001, 1, 40)
        self.programs["new"]["lightPos"]      = (mouse_x, mouse_y, 0.075)

        # Ambient colour
        ##########################################
        self.programs["new"]["ambientColour"]    = (225/225, 225/255, 225/255)
        self.programs["new"]["ambientIntensity"] = 58/225
        
        # Light Colour, you may change as you wish
        ##########################################
        self.programs["new"]["lightColour"]   = (196/225, 204/255, 67/255)
        #self.programs["new"]["lightColour"]   = (102/225, 36/255, 138/255)
        #self.programs["new"]["lightColour"]   = (255/225, 225/255, 225/255)

        super().update()

    def draw(self):

        # Draw content shenanigans
        self.framebuffers["new"].use()
        self.textures["main"].use(location=0)
        self.textures["normal"].use(location=1)
        self.programs["new"]["uTexture"] = 0
        self.programs["new"]["uNormal"]  = 1
        self.vaos["new"].render(mgl.TRIANGLE_STRIP)

        self.textures["new"].use(location=0)
        self.programs["main"]["uTexture"] = 0
        super().draw()
        

if __name__ == "__main__":
    ShaderProgram(
        media=r"_images\2TexturePlayer.png",
        caption="22/11/23",
        swizzle="RGBA",
        components=4,
        scale=24,
        flip=True
    ).run()