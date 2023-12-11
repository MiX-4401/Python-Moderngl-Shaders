"""
Author: Ethan.R
Date of Creation: 24th November 2023
Date of Release: NA
"""


from _lib import Main
import moderngl as mgl
import pygame
import numpy as np

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
    program_frag: str = """
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

uniform sampler2D tTexture;
uniform sampler2D tNormal;
uniform vec2 resolution;
uniform float time;

in vec2 uvs;
out vec4 fColour;

void main() {

    vec4 iAlbedo = texture(tTexture, uvs).rgba;
    vec3 iNormal = texture(tNormal, uvs).rgb;
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

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle)
        
        self.load_program()

        # Load lights
        self.ambient_light: AmbientLight = AmbientLight(colour=(255, 255, 255, 10))
        self.lights: tuple = (Light(colour=(176, 34, 60), pos=(0.1, 0.0)), Light(colour=(45, 196, 255), pos=(0.9, 1.0)))
        
        # Get light data
        self.ambient_data: np.array = self.ambient_light.get_data()
        self.light_data: np.array = Light.get_data()

        # Create light Uniform buffer object (UBO)
        self.light_buffer:   mgl.Buffer = self.ctx.buffer(self.light_data.tobytes())
        self.ambient_buffer: mgl.Buffer = self.ctx.buffer(self.ambient_data.tobytes())
        
        # Load normal texture
        normal_image_data = self.get_image_from_file(path=r"04Projects\ShaderShenanigans\images\0NormalWall.png", scale=1.5, flip=True)
        self.normal_texture: mgl.Texture  = self.get_texture_from_data(image_data=normal_image_data)
        self.normal_texture.filter: tuple = (mgl.NEAREST, mgl.NEAREST)

        # Load render target texture
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.new_texture.filter: tuple    = (mgl.NEAREST, mgl.NEAREST)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Create shader program
        self.new_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.new_vao:     mgl.VertexArray = self.ctx.vertex_array(self.new_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])


    @Main.d_update
    def update(self):
        self.new_program["resolution"].value = self.screen.get_size()
        self.new_program["time"].value = self.time

    @Main.d_garbage_cleanup
    def garbage_cleanup(self):
        self.light_buffer.release()
        self.normal_texture.release()
        self.ambient_buffer.release()

        self.new_texture.release()
        self.framebuffer.release()
        self.new_program.release()
        self.new_vao.release()


    @Main.d_draw
    def draw(self):
        self.framebuffer.clear(red=0.0, green=0.0, blue=0.0)
        self.framebuffer.use()

        self.light_buffer.bind_to_uniform_block(binding=0)
        self.ambient_buffer.bind_to_uniform_block(binding=1)
        self.my_texture.use(location=2)
        self.normal_texture.use(location=3)

        self.new_program["LightsBlock"].binding = 0
        self.new_program["AmbientLightBlock"].binding = 1
        self.new_program["tTexture"].value = 2
        self.new_program["tNormal"].value  = 3
        self.new_vao.render(mode=mgl.TRIANGLE_STRIP)

        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0)
        self.ctx.screen.use()
        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0


if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        path=r"04Projects\ShaderShenanigans\images\0TextureWall.png",
        caption="NA",
        swizzle="RGBA",
        scale=1.5,
        flip=True
    ).run()