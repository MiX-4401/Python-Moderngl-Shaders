"""
Author: Ethan.R
Date of Creation: 24th November 2023
Date of Release: NA
"""


from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):
    program_frag: str = """
# version 460 core

uniform sampler2D myTexture;


in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 colour = texture(myTexture, uvs).rgba;

    fColour = vec4(colour.rgb, colour.a);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle)

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
        pass

    @Main.d_draw
    def draw(self):
        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()
        self.my_texture.use(location=0)
        self.main_program["myTexture"] = 0


if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        caption="NA",
        swizzle="RGBA",
        scale=1,
        flip=False,
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Beautiful-landscape.png/800px-Beautiful-landscape.png"
    ).run()