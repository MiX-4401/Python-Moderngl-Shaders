"""
Author: Ethan.R
Date of Creation: 7th January 2024
Date of Release: NA
Creation Name: Rain Effect
Source: https://shadered.org/view?s=6Gny24_ojD
"""


from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):
    program_frag: str = """
# version 460 core

uniform sampler2D myTexture;
uniform vec2 uResolution;
uniform float utime;

in vec2 uvs;
out vec4 fColour;

void main(){

    float time  = utime * 0.004;

    vec4 colour1 = vec4(81.0/225.0, 179.0/225.0, 214.0/225.0, 1.0);
    vec4 colour2 = vec4(70.0/225.0, 126.0/225.0, 214.0/225.0, 1.0);
    vec4 colour3 = vec4(50.0/225.0, 82.0/225.0,  209.0/225.0, 1.0);
    vec4 colour4 = vec4(29.0/225.0, 48.0/225.0,  122.0/225.0, 1.0);

    // Pixelate effect
    vec2 uv_pixel = floor(uvs * (uResolution/4)) / (uResolution/4);
    //uv_pixel = uvs;

    vec3 displace = texture(myTexture, vec2(uv_pixel.x, (uv_pixel.y + time) * 0.05)).rgb;
    //displace = texture(myTexture, vec2(uv_pixel.x, (uv_pixel.y))).rgb;


    vec2 uv_temp = uv_pixel;
    uv_temp.y *= 0.2;
	uv_temp.y += time;
    vec4 colour = texture(myTexture, uv_temp + displace.xy);

    
    
    vec4 noise  = floor(colour * 10.0) / 5.0;
    vec4 bright = mix(colour1, colour2, uvs.y);
    vec4 dark   = mix(colour3, colour4, uvs.y);
    colour      = mix(dark, bright, noise);

    // Gradient 
    colour -= 0.45 * pow(uv_pixel.y, 8.0);
    colour += 0.5 * pow(1.0 - uv_pixel.y, 8.0);

    fColour = vec4(colour.rgb, colour.a);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None", headless:bool=False):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method, headless=headless)

        self.load_program()

        # Load render target texture
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Create shader program
        self.new_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.new_vao:     mgl.VertexArray = self.ctx.vertex_array(self.new_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])


    @Main.d_update
    def update(self):
        self.new_program["utime"] = self.time
        self.new_program["uResolution"] = self.screen.get_size()

    @Main.d_draw
    def draw(self):

        self.framebuffer.use()
        self.my_texture.use(location=0)
        self.new_program["myTexture"] = 0
        self.new_vao.render(mgl.TRIANGLE_STRIP)

        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()

        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0

if __name__ == "__main__":    
    shader_program: ShaderProgram = ShaderProgram(
        caption="Rain Effect",
        swizzle="RGBA",
        scale=1.0,
        flip=True,
        components=4,
        headless=True,
        method="linear",
        path=r"C:\Users\ejrad\OneDrive\Pictures\Ethan-PC Pictures\Custome screensavers\Rain Effect\image.png",
    ).run()



