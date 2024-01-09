"""
Author: Ethan.R
Date of Creation: 7th January 2024
Date of Release: NA
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

    vec2 uv_pixel = floor(uvs * (uResolution/4)) / (uResolution/4);
    uv_pixel = uvs;

    vec3 displace = texture(myTexture, vec2(uv_pixel.x, (uv_pixel.y + time) * 0.05)).rgb;

    vec2 uv_temp = uv_pixel;
    //uv_temp.y *= 0.2;
	//uv_temp.y += time;
    vec4 colour = texture(myTexture, uv_temp + displace.xy);

    fColour = vec4(colour);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)

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
        caption="NA",
        swizzle="RGBA",
        scale=0.5,
        flip=False,
        components=4,
        url="https://ragingnexus.com/assets/86c5a3-e4598871c3b71818c250cbb80c6ce1c08fbf501dc381137e0ebedd4951f0e946d0ef90d16201c054be9f3dce44b7234b3dc7572973665b2b3945e2dce784ded7.png",
    ).run()