"""
Author: Ethan.R
Date: 18th November 2023
"""

from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):

    program_frag: str = """
# version 460 core

uniform sampler2D myTexture;
uniform sampler2D normalTexture;
uniform vec2 resolution;
uniform vec3 fallOff;
uniform vec3 lightPos;
uniform vec3 lightColour;
uniform vec3 ambientColour;
uniform float ambientIntensity;

in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 tAlbedo = texture(myTexture, uvs).rgba;
    vec3 tNormal = texture(normalTexture, uvs).rgb;

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

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)

        # Load parent variables
        self.load_program()

        # Load normal texture
        normal_image_data = self.get_image_from_file(scale=24, flip=True, path=r"04Projects\ShaderShenanigans\images\2NormalPlayer.png")
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
        
        mouse_x: int = round(pygame.mouse.get_pos()[0], 2) / self.screen.get_size()[0]
        mouse_y: int = round(pygame.mouse.get_pos()[1], 2) / self.screen.get_size()[1]
        self.new_program["resolution"]    = self.screen.get_size()
        self.new_program["fallOff"]       = (0.00001, 1, 40)
        self.new_program["lightPos"]      = (mouse_x, mouse_y, 0.075)

        # Ambient colour
        ##########################################
        self.new_program["ambientColour"]    = (225/225, 225/255, 225/255)
        self.new_program["ambientIntensity"] = 58/225
        
        # Light Colour, you may change as you wish
        ##########################################
        self.new_program["lightColour"]   = (196/225, 204/255, 67/255)
        #self.new_program["lightColour"]   = (102/225, 36/255, 138/255)
        #self.new_program["lightColour"]   = (255/225, 225/255, 225/255)

    @Main.d_garbage_cleanup
    def garbage_cleanup(self):
        self.new_texture.release()
        self.framebuffer.release()
        self.new_program.release()
        self.new_vao.release()

        self.normal_texture.release()

    @Main.d_draw
    def draw(self):
        self.framebuffer.use()
        self.framebuffer.clear(red=0.0, green=0.0, blue=0.0)
        
        # Use textures
        self.my_texture.use(location=0)
        self.normal_texture.use(location=1)

        # Set shader uniforms
        self.new_program["myTexture"]     = 0
        self.new_program["normalTexture"] = 1

        # Render framebuffer
        self.new_vao.render(mgl.TRIANGLE_STRIP)

        # Set main shader uniforms
        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0

ShaderProgram(
    path=r"04Projects\ShaderShenanigans\images\2TexturePlayer.png",
    caption="22/11/23",
    swizzle="RGBA",
    scale=24
).run()