"""
Author: Ethan.R
Date: 17th November 2023
"""

from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):

    program_frag: str = """
# version 460 core

uniform sampler2D myTexture;
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

    vec4 colour      = texture(myTexture, uvs).rbga;
    vec4 finalColour = get_sepia(colour) - 0.09;
    //vec4 finalColour = colour;
    finalColour.rgb  = mix(finalColour.rgb, finalColour.rgb + vec3(noise_value), 0.19);

    fColour = vec4(finalColour.rgb, finalColour.a) * (1 - vigIntensity);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components)

        # Load parent variables
        self.load_program()

        # Create shader program
        self.new_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.new_vao:     mgl.VertexArray = self.ctx.vertex_array(self.new_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        self.new_program["resolution"] = self.screen.get_size()


    @Main.d_update
    def update(self):
        self.new_program["time"] = self.time

    @Main.d_draw
    def draw(self):
        self.framebuffer.clear(red=0.0, green=0.0, blue=0.0)

        self.framebuffer.use()
        self.my_texture.use(location=0)
        self.new_program["myTexture"] = 0
        self.new_vao.render(mgl.TRIANGLE_STRIP)

        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0

    @Main.d_garbage_cleanup
    def garbage_cleanup(self):
        self.new_texture.release()
        self.framebuffer.release()
        self.new_program.release()
        self.new_vao.release()

ShaderProgram(
    url=r"https://pre00.deviantart.net/949a/th/pre/i/2013/044/0/d/the_kookaburra_by_kqeina-d5us1tb.png",
    caption="20/11/23",
    swizzle="RBGA",
    scale=1
).run()