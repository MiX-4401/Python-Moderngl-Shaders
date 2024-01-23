"""
Author: Ethan.R
Date of Creation: 17th January 2024
Date of Release: NA
Name of Program: Shimmer Effect
"""


from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):
    program_frag: str = """
# version 460 core

uniform sampler2D myTexture;
uniform float uTime;

in vec2 uvs;
out vec4 fColour;

void main(){
    float time = uTime * 0.04;
    vec4 colour = vec4(1.0);

    if (uvs.y > 0.3){
        colour = texture(myTexture, vec2(uvs.x, -uvs.y));
    } else {
        float xoffset = 0.005 * cos(time * 3.0 + 200.0 * uvs.y);
        float yoffset = ((0.3 - uvs.y) / 0.3) * 0.05 * (1.0 + cos(time * 3.0 + 5.0 * uvs.y));

        colour = texture(myTexture, vec2(uvs.x + xoffset, -1.0 * (0.6 - uvs.y + yoffset)));
    }
    
    fColour = vec4(colour.rgb, 1.0);
    
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)

        self.load_program()

         # Load render target texture
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.new_texture.filter: tuple    = (mgl.NEAREST, mgl.NEAREST)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Create shader program
        self.new_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.new_vao:     mgl.VertexArray = self.ctx.vertex_array(self.new_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

    @Main.d_update
    def update(self):
        self.new_program["uTime"] = self.time

    def garbage_cleanup(self):
        super().garbage_cleanup() # A better way then using decorators in this context
        self.new_program.release()
        self.new_program.release()
        self.framebuffer.release()
        self.new_vao.release()
        self.new_texture.release()

    @Main.d_draw
    def draw(self):
        self.framebuffer.use()
        self.framebuffer.clear()
        self.my_texture.use(location=0)
        self.new_program["myTexture"] = 0
        self.new_vao.render(mgl.TRIANGLE_STRIP)

        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()

        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0


if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        caption="Shimmer Effect",
        swizzle="RGBA",
        scale=0.5,
        flip=False,
        components=3,
        url=r"https://chrismartinphotography.files.wordpress.com/2012/05/vermilion-river-c2a9-2012-christopher-martin-9748.jpg"
    ).run()