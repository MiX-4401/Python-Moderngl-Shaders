"""
Author: Ethan.R
Date of Creation: 31st January 2024
Date of Release: NA
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame as pg
import numpy as np

from _shaderPasses.bloom          import Bloom
from _shaderPasses.gaussianBlur   import GaussianBlur
from _shaderPasses.colourQuantise import ColourQuantise
from _shaderPasses.dithering      import Dithering
from _shaderPasses.sobelFilter    import SobelFilter
from _shaderPasses.contrast       import Contrast

class Light():
    instances: list = []
    def __init__(self, colour:tuple, pos:tuple):
        self.colour:   tuple = (colour[0]/225, colour[1]/225, colour[2]/225, 0.0)
        self.pos:      tuple = (pos[0], pos[1], 0.075, 0.0)
        self.fall_off: tuple = (1.0, 1.0, 1.0, 0.0)
        Light.instances.append(self)

    @classmethod
    def get_data(cls):
        light_data: np.array = np.zeros(shape=2, dtype=[("colour", "f4", 4), ("pos", "f4", 4), ("fallOff", "f4", 4)])
        for i,light in enumerate(cls.instances):
            light_data[i]["colour"]:  tuple = light.colour
            light_data[i]["pos"]:     tuple = light.pos
            light_data[i]["fallOff"]: tuple = light.fall_off

        return light_data

class AmbientLight():
    def __init__(self, colour:tuple):
        self.colour: tuple = (colour[0]/225, colour[1]/225, colour[2]/225, colour[3]/225)
    
    def get_data(self):
        return np.array(self.colour, dtype="f4")

class ShaderProgram(Main):
    frag: str = """
    # version 460 core


    struct Light {
        vec3 colour;
        vec3 pos;
        vec3 fallOff;
    };

    struct AmbientLight {
        vec4 colour;
    };

    layout(std140) uniform AmbientLightBlock {
        AmbientLight ambientLight[1];
    };

    layout(std140) uniform LightsBlock{
        Light lights[2];
    };

    uniform sampler2D uTexture;
    uniform sampler2D uNormal;
    uniform vec2 resolution;
    uniform float time;

    in vec2 uvs;
    out vec4 fColour;

    void main() {

        vec4 iAlbedo = texture(uTexture, uvs).rgba;
        vec3 iNormal = texture(uNormal, uvs).rgb;
        vec3 normal = normalize(iNormal * 2.0 - 1.0);
        
        vec4 ambientColour = ambientLight[0].colour.rgba;
        vec3 finalColour = ambientColour.rgb * ambientColour.a;

        for (int i=0; i < 2; i++) {
            Light light  = lights[i];
            vec3 colour  = light.colour;
            vec3 pos     = light.pos;
            vec3 fallOff = light.fallOff;

            if (i==1){
                pos.y += sin(time * 0.01);
            }
            else {
                pos.y += 1 - sin(time * 0.01);
            };

            vec3 lightDir  = vec3(pos.xy - (gl_FragCoord.xy / resolution.xy), pos.z);
            lightDir.x    *= resolution.x / resolution.y;
            vec3 ray       = normalize(lightDir);
            float distance = length(lightDir);

            vec3 diffuse = colour * max(dot(normal, ray), 0.0);
            float attenuation = 1.0 / (fallOff.x + (fallOff.y * distance) + (fallOff.z * distance * distance));
            finalColour += diffuse * attenuation;
        }
        
        fColour = vec4(iAlbedo.rgb * finalColour, 1.0);
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

        # Load lights
        self.ambient_light: AmbientLight = AmbientLight(colour=(255, 255, 255, 10))
        self.lights: tuple = (Light(colour=(176, 34, 60), pos=(0.1, 0.0)), Light(colour=(45, 196, 255), pos=(0.9, 1.0)))

        # Get light data
        self.ambient_data: np.array = self.ambient_light.get_data()
        self.light_data: np.array = Light.get_data()

        # Create light Uniform buffer object (UBO)
        self.create_buffer(title="light", data=self.light_data.tobytes())
        self.create_buffer(title="ambient", data=self.ambient_data.tobytes())

        # Load normal texture
        self.create_texture(title="normal", size=self.content.size, components=self.components)
        self.textures["normal"].write(data=self.get_image_data_from_file(path=r"_images\0NormalWall.png", scale=1.5, flip=True))

    def update(self):
        # Update content shenanigans
        self.programs["new"]["resolution"].value = self.screen.get_size()
        self.programs["new"]["time"].value = self.time
        super().update()

    def draw(self):

        self.framebuffers["new"].clear(red=0.0, green=0.0, blue=0.0)
        self.framebuffers["new"].use()

        self.buffers["light"].bind_to_uniform_block(binding=0)
        self.buffers["ambient"].bind_to_uniform_block(binding=1)
        self.textures["main"].use(location=2)
        self.textures["normal"].use(location=3)

        self.programs["new"]["LightsBlock"].binding = 0
        self.programs["new"]["AmbientLightBlock"].binding = 1
        self.programs["new"]["uTexture"].value = 2
        self.programs["new"]["uNormal"].value  = 3
        self.vaos["new"].render(mode=mgl.TRIANGLE_STRIP)

        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0)
        self.ctx.screen.use()
        self.framebuffers["new"].color_attachments[0].use(location=0)
        self.programs["main"]["uTexture"] = 0

        super().draw()
        

if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        media=r"_images\0TextureWall.png",
        caption="NA",
        swizzle="RGBA",
        scale=1.5,
        flip=True,
        components=4,
    ).run()